import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.tsx";
import "./index.css";
import { AuthProvider } from "./context/auth-context.tsx";
import { CartProvider } from "./context/cart-context.tsx";
import { Toaster } from "sonner";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {/* Bọc BrowserRouter để kích hoạt routing */}
    <BrowserRouter>
      {/* Bọc AuthProvider để quản lý đăng nhập */}
      <AuthProvider>
        {/* Bọc CartProvider để quản lý giỏ hàng */}
        <CartProvider>
          <App />
          <Toaster richColors position="top-right" />
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);