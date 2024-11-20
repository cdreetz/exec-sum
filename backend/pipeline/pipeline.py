import base64
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dataclasses import dataclass
from openai import AzureOpenAI
from typing import List, Dict, Any
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Output document sections
# Section 1: Water (floods, ports)
# Section 2: Fire (wildfires, fire stations)
# Section 3: Administrative (employees, establishments, admin supprt, etc.)
# Section 4: Other (anything else)

class Document:
    def __init__(self, sections: Dict[str, str], tables: List[Dict[str, Any]] = None):
        self.sections = sections
        self.tables = tables or []


class DocumentProcessor:
    def __init__(self, doc_client, openai_client):
        self.doc_client = doc_client
        self.openai_client = openai_client

    def process_document(self, pdf_path, example_document):
        """Extract text from a PDF file and process it into sections"""
        content, tables = self._extract_content(pdf_path)
        
        section_chunks = {}
        for chunk in content:
            if chunk.get('role') == 'table':
                table_index = chunk.get('table_index')
                table_summary = tables[table_index]['metadata']['summary']
                section = self._ask_gpt_which_section(
                    chunk['text'],
                    is_table=True,
                    table_summary=table_summary
                )
                if section not in section_chunks:
                    section_chunks[section] = []
                section_chunks[section].append({
                    'text': chunk['text'],
                    'is_table': True,
                    'table_index': table_index
                })
            else:
                section = self._ask_gpt_which_section(chunk['text'])
                if section not in section_chunks:
                    section_chunks[section] = []
                section_chunks[section].append({
                    'text': chunk['text'],
                    'is_table': False
                })

        sections = {}
        for section_name, section_content in section_chunks.items():
            example_content = example_document.sections.get(section_name)
            sections[section_name] = self._generate_section(section_content, example_content, tables)

        return Document(sections, tables)

    def _extract_content(self, pdf_path):
        """Extract and process content from a PDF file"""
        with open(pdf_path, "rb") as doc:
            file_content = doc.read()
            file_content_base64 = base64.b64encode(file_content).decode("utf-8")

        analyze_request = {
            "base64Source": file_content_base64
        }
        poller = self.doc_client.begin_analyze_document(
            "prebuilt-layout", 
            analyze_request=analyze_request
        )
        result = poller.result()

        # Get spans of all tables
        table_spans = []
        for table in result.tables:
            if len(table.cells) > 0:
                table_spans.append((table.spans[0].offset, table.spans[0].offset + table.spans[0].length))

        # Filter paragraphs to exclude table content
        content = []
        tables = []  # New list to store table data separately

        for paragraph in result.paragraphs:
            # Check if paragraph overlaps with any table
            para_start = paragraph.spans[0].offset
            para_end = para_start + paragraph.spans[0].length
            
            is_in_table = any(
                (table_start <= para_start < table_end) or 
                (table_start < para_end <= table_end)
                for table_start, table_end in table_spans
            )
            
            if not is_in_table:
                content.append({
                    'text': paragraph.content,
                    'role': paragraph.role
                })

        # Updated table processing
        for table in result.tables:
            if len(table.cells) > 0:
                headers = [cell.content.strip() for cell in table.cells[0]]
                table_content = {
                    'headers': headers,
                    'rows': []
                }
                
                for row_cells in table.cells[1:]:
                    row_data = {}
                    for header, cell in zip(headers, row_cells):
                        row_data[header] = cell.content.strip()
                    table_content['rows'].append(row_data)
                
                table_data = {
                    'content': table_content,
                    'metadata': {
                        'summary': None,
                        'description': None
                    }
                }
                table_data['metadata']['summary'] = self._generate_table_summary(table_data)

                tables.append(table_data)  # Store structured table data
                # Add table reference to content for section classification
                content.append({
                    'text': f"Table with columns: {', '.join(headers)}",
                    'role': 'table',
                    'table_index': len(tables) - 1
                })

        return content, tables

    def _ask_gpt_which_section(self, text, is_table=False, table_summary=None):
        """Ask GPT which section the text belongs to"""
        base_prompt = f"""Which section does the following text belong to? Options are:
        - Water (floods, ports)
        - Fire (wildfires, fire stations)
        - Administrative (employees, establishments, admin support, etc.)
        - Other (anything else)"""

        if is_table:
            prompt = f"""{base_prompt}
            This is a table. Here's it's summary:
            {table_summary}
            Return only the section name, nothing else."""

        else:
            prompt = f"""{base_prompt}

            Text: {text}

            Return only the section name, nothing else."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    def _generate_section(self, section_content, example_content, tables):
        # Modify content processing to handle table references
        processed_content = []
        for chunk in section_content:
            if chunk['is_table']:
                table = tables[chunk['table_index']]
                table_summary = table['metadata']['summary']
                processed_content.append(f"[Table {chunk['table_index']}: {table_summary}]")
            else:
                processed_content.append(chunk['text'])

        prompt = f"""Generate a section using these text chunks as source material.
        Here's an example of what the section should look like:
        {example_content}

        Source chunks:
        {' '.join(processed_content)}

        When referring to tables, incorporate the table information naturally into the narrative."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    def _generate_table_summary(self, table_data):
        """Generate a summary description for a table"""
        headers = table_data['content']['headers']
        example_rows = table_data['content']['rows'][:3]
        prompt = f"""Analyze this table and provide a brief summary of its purpose and content.

        Table Headers: {', '.join(headers)}
        Example Rows:
        {json.dumps(example_rows, index=2)}

        Provide a concise summary (2-3 sentences) that explains:
        1. What this table appears to be tracking or documenting
        2. What key information the columsn contain
        """
        response = self.openai_client.chat.completions.create(
            model="gpt-40-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()



class DocumentEvaluator:
    def __init__(self, openai_client: AzureOpenAI):
        self.openai_client = openai_client

    def compare_documents(self, generated_document, example_document):
        scores = {}
        for section_name in example_document.sections:
            if section_name in generated_document.sections:
                scores[section_name] = self._compare_sections(
                    generated_document.sections[section_name],
                    example_document.sections[section_name]
                )
            else:
                scores[section_name] = 0

        return {
            'section_scores': scores,
            'overall_score': sum(scores.values()) / len(scores)
        }

    def _compare_sections(self, generated_section, example_section):
        prompt = f"""Compare these two sections and rate the generated section on a scale of 1 to 10.
        Here's the example section:
        {example_section}

        Here's the generated section:
        {generated_section}

        Return only the score, nothing else."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return float(response.choices[0].message.content.strip())
            


def main():
    doc_client = DocumentIntelligenceClient(
        endpoint=os.getenv("AZURE_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("AZURE_API_KEY"))
    )

    openai_client = AzureOpenAI(
        api_version="2024-08-01-preview",
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )

    # Example document 
    example_document = Document({
        "Water": """The region faces significant water-related challenges. Recent flooding 
        has affected coastal areas, particularly around Port Harbor where infrastructure 
        damage was reported at three major terminals. Flood control measures implemented 
        last year have shown mixed results. The port authority has initiated a $2M project 
        to upgrade flood barriers.""",
        
        "Fire": """Fire services have been enhanced with two new stations in the western 
        district. The wildfire response team conducted 12 major operations this period, 
        successfully containing fires before they reached residential areas. Station 
        equipment upgrades are ongoing, with 5 new trucks deployed.""",
        
        "Administrative": """Current staff levels include 342 full-time employees across 
        15 facilities. Administrative support services have been consolidated into 3 main 
        centers. Employee training programs reached 89% completion rate. New establishment 
        records show 27 auxiliary offices operating under revised protocols.""",
        
        "Other": """Miscellaneous developments include the implementation of new software 
        systems and updated security protocols. Various community engagement initiatives 
        were launched. External contractor relationships have been reviewed and updated 
        per standard procedures."""
    })

    pipeline = DocumentProcessor(doc_client, openai_client)
    evaluator = DocumentEvaluator(openai_client)

    generated_document = pipeline.process_document("documents/AdminProvisions.pdf", example_document)
    evaluation = evaluator.compare_documents(generated_document, example_document)
    print(f"Overall score: {evaluation['overall_score']}")
    print("\nSection scores:")
    for section_name, score in evaluation['section_scores'].items():
        print(f"{section_name}: {score}")

    # Example output:
    # Overall score: 3.25

    # Section scores:
    # Water: 0
    # Fire: 0
    # Administrative: 6.0
    # Other: 7.0

if __name__ == "__main__":
    main()