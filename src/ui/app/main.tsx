// src/ui/app/main.tsx
import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Auth0Provider } from "@auth0/auth0-react";
import { App } from "./App";

const container = document.getElementById("root");

if (!container) {
  throw new Error("Root container missing");
}

const root = createRoot(container);
root.render(
  <Auth0Provider
    domain="dev-wq48vbh0vsb4izgn.us.auth0.com"
    clientId="IBJ9kugJpqwQfzoqNywLBAowFWOzNDOV"
    authorizationParams={{ redirect_uri: window.location.origin }}
  >
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </Auth0Provider>
);
