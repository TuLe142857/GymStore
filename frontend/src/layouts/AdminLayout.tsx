import React from "react";
import { Outlet, NavLink } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  Layers,
  BookOpen,
  ArrowLeft,
  LogOut,
} from "lucide-react";

const AdminLayout: React.FC = () => {
  const { logout } = useAuth();

  const navItemClass = ({ isActive }: { isActive: boolean }) =>
      `
    flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition
    ${isActive
          ? "bg-gray-800 text-white"
          : "text-gray-300 hover:bg-gray-800 hover:text-white"}
  `;

  return (
      <div className="flex min-h-screen bg-gray-100">
        {/* Sidebar */}
        <aside className="w-64 bg-gradient-to-b from-gray-900 to-gray-800 text-white p-6 flex flex-col">
          <h2 className="text-2xl font-bold mb-8 tracking-wide">
            Admin Panel
          </h2>

          <nav className="flex-1 space-y-2">
            <NavLink to="/admin/statistics" className={navItemClass}>
              <LayoutDashboard size={18} />
              Statistic
            </NavLink>

            <NavLink to="/admin/orders" className={navItemClass}>
              <ShoppingCart size={18} />
              Orders
            </NavLink>

            <NavLink to="/admin/products" className={navItemClass}>
              <Package size={18} />
              Products
            </NavLink>

            <NavLink to="/admin/catalogs" className={navItemClass}>
              <Layers size={18} />
              Catalogs
            </NavLink>

            <NavLink to="/admin/training" className={navItemClass}>
              <BookOpen size={18} />
              Training
            </NavLink>

            <NavLink to="/" className={navItemClass}>
              <ArrowLeft size={18} />
              Back to site
            </NavLink>
          </nav>

          <Button
              onClick={logout}
              className="mt-6 w-full bg-red-600 hover:bg-red-700 flex items-center gap-2"
          >
            <LogOut size={16} />
            Log out
          </Button>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6">
          <div className="bg-white rounded-xl shadow p-6 min-h-full">
            <Outlet />
          </div>
        </main>
      </div>
  );
};

export default AdminLayout;
