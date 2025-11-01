import { Link, useNavigate } from "react-router-dom";
import { ShoppingCart, User, Package, LogOut, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";
import { useCart } from "@/context/cart-context";

export default function Header() {
  const { isLoggedIn, role, logout } = useAuth(); // ✅ lấy role từ context
  const { itemCount } = useCart();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link
          to="/"
          className="flex items-center gap-2 font-bold text-xl text-primary"
        >
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground font-bold">
            GS
          </div>
          <span>GymStore</span>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <Link
            to="/"
            className="text-sm font-medium hover:text-primary transition-colors"
          >
            Home
          </Link>
          <Link
            to="/products"
            className="text-sm font-medium hover:text-primary transition-colors"
          >
            Products
          </Link>
          <Link
            to="/about"
            className="text-sm font-medium hover:text-primary transition-colors"
          >
            About
          </Link>

          {/* ✅ Admin Panel - chỉ hiện khi role là ADMIN */}
          {isLoggedIn && role === "ADMIN" && (
            <Link
              to="/admin/orders"
              className="flex items-center gap-1 text-red-500 font-semibold hover:text-red-700 transition"
              title="Go to Admin Dashboard"
            >
              <Settings className="w-4 h-4" />
              Admin Panel
            </Link>
          )}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-4">
          {isLoggedIn ? (
            <>
              <Link to="/orders">
                <Button variant="ghost" size="icon" title="Orders">
                  <Package className="w-5 h-5" />
                </Button>
              </Link>
              <Link to="/profile">
                <Button variant="ghost" size="icon" title="Profile">
                  <User className="w-5 h-5" />
                </Button>
              </Link>
              <Button
                variant="ghost"
                size="icon"
                title="Logout"
                onClick={handleLogout}
              >
                <LogOut className="w-5 h-5" />
              </Button>
            </>
          ) : (
            <Link to="/login">
              <Button variant="ghost" size="sm">
                Sign In
              </Button>
            </Link>
          )}

          {/* Giỏ hàng */}
          <Link to="/cart">
            <Button
              variant="ghost"
              size="icon"
              title="Shopping Cart"
              className="relative"
            >
              {isLoggedIn && itemCount > 0 && (
                <span className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center">
                  {itemCount}
                </span>
              )}
              <ShoppingCart className="w-5 h-5" />
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
