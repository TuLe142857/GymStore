import { useEffect, useState } from "react";
import axiosClient from "@/utils/axiosClient";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import { useCart } from "@/context/cart-context"; // Import useCart

export default function CartPage() {
  const [cart, setCart] = useState<any>(null);
  const navigate = useNavigate(); // Sử dụng hook
  const { fetchCartCount } = useCart(); // Lấy hàm cập nhật số lượng

  const loadCart = async () => {
    try {
      const res = await axiosClient.get("/cart/");
      setCart(res.data);
    } catch (error) {
      console.error("Failed to load cart", error);
    }
  };

  useEffect(() => {
    loadCart();
  }, []);

  const handleRemove = async (id: number) => {
    try {
      await axiosClient.delete(`/cart/item/${id}`);
      await loadCart(); // Tải lại dữ liệu giỏ hàng
      await fetchCartCount(); // Cập nhật lại số lượng trên header
    } catch (error) {
      console.error("Failed to remove item", error);
    }
  };

  if (!cart) return <p className="p-6">Loading cart...</p>;
  if (cart.items.length === 0)
    return <p className="p-6">Your cart is empty</p>;

  return (
    <div className="container mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">Your Cart</h1>
      <div className="space-y-4">
        {cart.items.map((item: any) => (
          <div
            key={item.id}
            className="flex flex-col md:flex-row justify-between border-b py-4"
          >
            <div className="flex gap-4 items-center mb-2 md:mb-0">
              <div>
                <p className="font-semibold">{item.product?.name}</p>
                <p className="text-muted-foreground text-sm">
                  Qty: {item.quantity}
                </p>
              </div>
            </div>
            <div className="flex gap-4 items-center justify-between">
              <p className="font-medium text-lg">
                {Intl.NumberFormat("vi-VN").format(Number(item.product?.price))} VND
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleRemove(item.id)}
              >
                Remove
              </Button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <p className="text-2xl font-bold">
          Total {Intl.NumberFormat("vi-VN").format(Number(cart.total_price))} VND
        </p>
        <Button
          size="lg"
          onClick={() => navigate("/checkout")} // Sử dụng navigate
        >
          Proceed to Checkout
        </Button>
      </div>
    </div>
  );
}