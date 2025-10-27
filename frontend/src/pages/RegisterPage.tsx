import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import axiosClient from "@/utils/axiosClient";
import { ArrowLeft, Mail, Key, User } from "lucide-react";

export default function RegisterPage() {
  const [step, setStep] = useState(1); // 1: Email, 2: OTP, 3: Info
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [registrationToken, setRegistrationToken] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(0);
  const navigate = useNavigate();

  // countdown cooldown resend OTP
  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  // --- Step 1: gửi OTP đến email ---
  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !email.includes("@")) {
      setError("Please enter a valid email address.");
      return;
    }

    try {
      setLoading(true);
      await axiosClient.post("/auth/verify", { email });
      setStep(2);
      setCooldown(60);
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to send OTP. Try again.");
    } finally {
      setLoading(false);
    }
  };

  // --- Step 2: xác thực OTP ---
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!otp || otp.length < 6) {
      setError("OTP must be at least 6 digits.");
      return;
    }

    try {
      setLoading(true);
      const res = await axiosClient.post("/auth/verify-confirm", { email, otp });
      const token = res.data?.data?.registration_token;
      if (!token) {
        setError("Invalid response from server. Missing registration token.");
        return;
      }
      setRegistrationToken(token);
      setStep(3);
    } catch (err: any) {
      setError(err.response?.data?.message || "Invalid OTP. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // --- Step 3: hoàn tất đăng ký ---
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!registrationToken) {
      setError("Registration session expired. Please start over.");
      setStep(1);
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    try {
      setLoading(true);
      const res = await axiosClient.post("/auth/register", {
        email,
        password,
        full_name: fullName,
        registration_token: registrationToken,
      });

      const accessToken = res.data?.data?.access_token;
      if (accessToken) {
        alert("Registration successful! Please sign in.");
        navigate("/login");
      } else {
        setError("Invalid response from server. Missing access token.");
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Registration failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const goBackToEmail = () => {
    setStep(1);
    setOtp("");
    setError(null);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-muted">
      <div className="w-full max-w-md p-8 space-y-6 bg-background shadow-lg rounded-lg">
        {/* STEP 1: nhập email */}
        {step === 1 && (
          <form onSubmit={handleSendOtp} className="space-y-4">
            <h1 className="text-3xl font-bold text-center">Create Account</h1>
            <p className="text-center text-muted-foreground">
              Enter your email to receive an OTP
            </p>

            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1">
                <Mail className="inline w-4 h-4 mr-1" /> Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setError(null);
                }}
                required
              />
            </div>

            {error && <p className="text-destructive text-sm">{error}</p>}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Sending OTP..." : "Send OTP"}
            </Button>
          </form>
        )}

        {/* STEP 2: nhập OTP */}
        {step === 2 && (
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <h1 className="text-3xl font-bold text-center">Verify Email</h1>
            <p className="text-center text-muted-foreground">
              We sent an OTP to <span className="font-medium">{email}</span>.
            </p>

            <div>
              <label htmlFor="otp" className="block text-sm font-medium mb-1">
                <Key className="inline w-4 h-4 mr-1" /> OTP Code
              </label>
              <Input
                id="otp"
                type="text"
                placeholder="123456"
                value={otp}
                onChange={(e) => {
                  setOtp(e.target.value);
                  setError(null);
                }}
                required
              />
            </div>

            {error && <p className="text-destructive text-sm">{error}</p>}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Verifying..." : "Verify OTP"}
            </Button>

            <div className="flex justify-between items-center text-sm">
              <Button
                variant="link"
                type="button"
                onClick={goBackToEmail}
                className="text-muted-foreground"
              >
                <ArrowLeft className="w-4 h-4 mr-1" /> Back
              </Button>

              <Button
                variant="link"
                type="button"
                onClick={handleSendOtp}
                disabled={cooldown > 0 || loading}
              >
                {cooldown > 0 ? `Resend OTP (${cooldown}s)` : "Resend OTP"}
              </Button>
            </div>
          </form>
        )}

        {/* STEP 3: nhập thông tin tài khoản */}
        {step === 3 && (
          <form onSubmit={handleRegister} className="space-y-4">
            <h1 className="text-3xl font-bold text-center">Final Step</h1>
            <p className="text-center text-muted-foreground">
              Email verified! Now create your account.
            </p>

            <Input
              type="email"
              value={email}
              disabled
              className="bg-muted"
            />

            <div>
              <label htmlFor="fullName" className="block text-sm font-medium mb-1">
                <User className="inline w-4 h-4 mr-1" /> Full Name
              </label>
              <Input
                id="fullName"
                type="text"
                placeholder="Your full name"
                value={fullName}
                onChange={(e) => {
                  setFullName(e.target.value);
                  setError(null);
                }}
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1">
                <Key className="inline w-4 h-4 mr-1" /> Password
              </label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError(null);
                }}
                required
              />
            </div>

            {error && <p className="text-destructive text-sm">{error}</p>}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creating Account..." : "Create Account"}
            </Button>
          </form>
        )}

        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link to="/login" className="font-medium hover:text-primary">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
