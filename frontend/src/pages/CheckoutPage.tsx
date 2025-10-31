import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import axiosClient from "@/utils/axiosClient";
import { logInteraction } from "@/utils/interactions";

export default function CheckoutPage() {
  const [address, setAddress] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // BƯỚC 1: LẤY GIỎ HÀNG TRƯỚC
      const cartRes = await axiosClient.get("/cart/");
      const cartItems = cartRes.data?.items || [];

      if (cartItems.length === 0) {
        alert("Your cart is empty!");
        setLoading(false);
        return;
      }

      // BƯỚC 2: TẠO ĐƠN HÀNG
      const res = await axiosClient.post("/order/create", {
        shipping_address: address,
      });

      console.log("Order response:", res.data);

      // BƯỚC 3: GHI LOG (dùng cartItems đã lấy từ Bước 1)
      for (const item of cartItems) {
        // Đảm bảo item.product.id tồn tại
        if (item.product && item.product.id) {
          logInteraction(String(item.product.id), "purchase");
        }
      }

      alert("Order placed successfully!");
      // Cập nhật lại context giỏ hàng (nếu có)
      // fetchCart(); // Ví dụ gọi lại hàm fetchCart từ context
      navigate("/orders");
    } catch (err: any) {
      console.error("Checkout error:", err);
      alert(err.response?.data?.error || "Checkout failed!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">Checkout</h1>
      <form onSubmit={handleCheckout} className="space-y-4 max-w-md">
        <Input
          placeholder="Enter shipping address"
          value={address}
          onChange={(e) => setAddress(e.target.value)} // ✅ sửa e.value -> e.target.value
          required
        />
        <Button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Place Order"}
        </Button>
      </form>
    </div>
  );
}
