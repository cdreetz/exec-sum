import { Configuration, PopupRequest } from "@azure/msal-browser";

const getRedirectUri = () => {
    const origin = window.location.origin;
    console.log("Redirect URI:", origin);
    return origin;
};

export const msalConfig: Configuration = {
    auth: {
        clientId: "b7f7685b-0995-44b7-9bc5-71260d2d9489",
        authority: "https://login.microsoftonline.com/f72ddd3c-9aa7-4871-a87f-009d8d3bd1c3",
        redirectUri: getRedirectUri(),
    },
    cache: {
        cacheLocation: "sessionStorage",
        storeAuthStateInCookie: false,
    },
};

export const loginRequest: PopupRequest = {
    scopes: ["user.read"],
};

console.log("Redirect Config:", JSON.stringify(msalConfig, null, 2));