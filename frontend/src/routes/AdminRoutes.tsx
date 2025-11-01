import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/auth-context";

export default function AdminRoute() {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="container mx-auto py-12 text-center">Loading user...</div>;
  }

  // Nếu đã login VÀ user.is_admin = true, cho phép truy cập
  if (isAuthenticated && user?.is_admin) {
    return <Outlet />; // Hiển thị các trang con (ví dụ: AdminOrdersPage)
  }

  // Nếu không, đá về trang chủ
  return <Navigate to="/" replace />;
}