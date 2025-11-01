import React from "react";
import { Outlet, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";

const AdminLayout: React.FC = () => {
  const { logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white p-6">
        <h2 className="text-xl font-bold mb-6">Admin Panel</h2>
        <nav className="space-y-3">
          <Link to="/admin/orders" className="block hover:text-primary">
            📦 Orders list
          </Link>
          <Link to="/" className="block hover:text-primary">
            🏠 Back
          </Link>
          <Button
            onClick={logout}
            className="mt-6 w-full bg-red-600 hover:bg-red-700"
          >
            Log out
          </Button>
        </nav>
      </aside>

      {/* Nội dung chính */}
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
};

export default AdminLayout;
