  import { useState } from "react";
  import { Link, useNavigate } from "react-router-dom";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import axiosClient from "@/utils/axiosClient";
  import { useAuth } from "@/context/auth-context"; // Import

  export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth(); // Sử dụng context

    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      setLoading(true);
      setError(null);

      try {
        // Giả sử API đăng nhập là /auth/login
        const res = await axiosClient.post("/auth/login", { email, password });
        
        if (res.data.data && res.data.data.access_token) {
          login(res.data.data.access_token); // Lưu token vào context
          navigate("/"); // Điều hướng về trang chủ
        } else {
          setError("Invalid login response from server.");
        }
      } catch (err: any) {
        console.error(err);
        setError(
          err.response?.data?.message || "Login failed. Please check your credentials."
        );
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="flex items-center justify-center min-h-screen bg-muted">
        <div className="w-full max-w-md p-8 space-y-6 bg-background shadow-lg rounded-lg">
          <h1 className="text-3xl font-bold text-center">Sign In</h1>
          <p className="text-center text-muted-foreground">
            Welcome back to GymStore
          </p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium mb-1"
              >
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium mb-1"
              >
                Password
              </label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && <p className="text-destructive text-sm">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing In..." : "Sign In"}
            </Button>
          </form>
          <p className="text-center text-sm text-muted-foreground">
            Don't have an account?{" "}
            <Link to="/signup" className="font-medium hover:text-primary">
              Sign Up
            </Link>
          </p>
        </div>
      </div>
    );
  }