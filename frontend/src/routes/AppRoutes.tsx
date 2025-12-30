import React from "react";
import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import DefaultLayout from "../layouts/DefaultLayout";
import { useAuth } from "@/context/auth-context"; // Import useAuth

import HomePage from "@/pages/HomePage";
import ProductsPage from "@/pages/ProductsPage";
import ProductPage from "@/pages/ProductPage"; // Bổ sung
import SearchPage from "@/pages/SearchPage";
import LoginPage from "@/pages/LoginPage"; // Bổ sung
import RegisterPage from "@/pages/RegisterPage"; // Bổ sung
import CartPage from "@/pages/CartPage";
import CheckoutPage from "@/pages/CheckoutPage";
import OrdersPage from "@/pages/OrderPage";
import ProfilePage from "@/pages/ProfilePage";
import OrderDetailPage from "@/pages/OrderDetailPage"; 
import AdminOrdersPage from "@/pages/admin/AdminOrdersPage";
import AdminProductsPage from "@/pages/admin/AdminProductsPage";
import AdminCatalogsPage from "@/pages/admin/AdminCatalogsPage";
import AdminStatisticsPage from "@/pages/admin/AdminStatisticsPage";
import AdminTrainingPage from "@/pages/admin/AdminTrainingPage";
import AdminLayout from "@/layouts/AdminLayout";
// ✅ Component bảo vệ route yêu cầu đăng nhập (đã cập nhật)
const ProtectedRoute: React.FC = () => {
  const { isLoggedIn } = useAuth(); // Sử dụng trạng thái từ context
  if (!isLoggedIn) return <Navigate to="/login" replace />;
  return <Outlet />;
};

const AdminProtectedRoute: React.FC = () => {
  const { isLoggedIn, role } = useAuth();
  if (!isLoggedIn) return <Navigate to="/login" replace />;
  if (role !== "ADMIN") return <Navigate to="/" replace />;
  return <Outlet />;
};

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Routes dùng DefaultLayout */}
      <Route element={<DefaultLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/product/:id" element={<ProductPage />} />
        <Route path="/search" element={<SearchPage />} />

        {/* 🔒 Các route yêu cầu đăng nhập */}
        <Route element={<ProtectedRoute />}>
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/orders/:id" element={<OrderDetailPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
      </Route>

      <Route element={<AdminProtectedRoute />}>
        <Route element={<AdminLayout />}>
            <Route path="/admin/orders" element={<AdminOrdersPage />} />
            <Route path="/admin/products" element={<AdminProductsPage />} />
            <Route path="/admin/catalogs" element={<AdminCatalogsPage />} />
            <Route path="/admin/statistics" element={<AdminStatisticsPage />} />
            <Route path="/admin/training" element={<AdminTrainingPage />} />
        </Route>
      </Route>

      {/* Auth routes (không cần layout) */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<RegisterPage />} />

      {/* Redirect unknown routes */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;