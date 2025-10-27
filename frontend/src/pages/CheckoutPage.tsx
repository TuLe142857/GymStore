import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import axiosClient from "@/utils/axiosClient";
import { logInteraction } from "@/utils/interactions"; // <-- 1. IMPORT HÀM MỚI

export default function CheckoutPage() {
  const [address, setAddress] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Khai báo kiểu dữ liệu tạm thời cho cart item
    type CartItem = {
      id: number;
      product: { id: string; name: string; };
      quantity: number;
    };

    try {
      // --- 2. LẤY GIỎ HÀNG TRƯỚC KHI THANH TOÁN ---
      // Dùng logic tương tự CartPage.tsx để lấy danh sách item
      const cartRes = await axiosClient.get("/cart/");
      const cartItems: CartItem[] = cartRes.data?.items || [];
      // ---------------------------------------------

      // 3. Tạo đơn hàng (như cũ)
      await axiosClient.post("/order/create", { shipping_address: address });

      // --- 4. LOG 'PURCHASE' CHO TỪNG SẢN PHẨM ---
      // Chạy sau khi tạo đơn hàng thành công
      if (cartItems.length > 0) {
        console.log("Logging 'purchase' interaction for items:", cartItems);
        for (const item of cartItems) {
          if (item.product?.id) {
            logInteraction(String(item.product.id), 'purchase');
          }
        }
      }
      // ------------------------------------------

      // 5. Điều hướng (như cũ)
      navigate("/orders");
    } catch {
      alert("Checkout failed");
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
          onChange={(e) => setAddress(e.value)}
          required
        />
        <Button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Place Order"}
        </Button>
      </form>
    </div>
  );
}