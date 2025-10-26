import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axiosClient from "@/utils/axiosClient";
import { useAuth } from "./auth-context"; // Sử dụng auth-context

// Định nghĩa kiểu dữ liệu cho context
interface CartContextType {
  itemCount: number;
  fetchCartCount: () => void;
  addToCart: (productId: string, quantity: number) => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

// Component Provider
export const CartProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [itemCount, setItemCount] = useState(0);
  const { isLoggedIn } = useAuth(); // Lấy trạng thái đăng nhập

  // Hàm gọi API để lấy số lượng sản phẩm trong giỏ hàng
  const fetchCartCount = async () => {
    if (!isLoggedIn) {
      setItemCount(0);
      return;
    }
    try {
      const res = await axiosClient.get("/cart/");
      // Đếm tổng số lượng sản phẩm
      const itemsArray = res.data.items || [];
      const count = itemsArray.reduce(
        (total: number, item: any) => total + item.quantity,
        0
      );
      setItemCount(count);
    } catch (error) {
      console.error("Failed to fetch cart count", error);
      setItemCount(0); // Đặt lại về 0 nếu có lỗi (ví dụ: token hết hạn)
    }
  };

  // Tải số lượng giỏ hàng khi component mount hoặc khi trạng thái đăng nhập thay đổi
  useEffect(() => {
    fetchCartCount();
  }, [isLoggedIn]);

  // Hàm gọi API để thêm sản phẩm vào giỏ hàng
  const addToCart = async (productId: string, quantity: number) => {
    if (!isLoggedIn) {
      alert("Please log in to add items to your cart.");
      return;
    }
    try {
      await axiosClient.post("/cart/add", {
        product_id: productId,
        quantity: quantity,
      });
      // Sau khi thêm thành công, gọi lại API để cập nhật số lượng
      await fetchCartCount();
    } catch (error) {
      console.error("Failed to add to cart", error);
      alert("Failed to add item to cart.");
    }
  };

  return (
    <CartContext.Provider value={{ itemCount, fetchCartCount, addToCart }}>
      {children}
    </CartContext.Provider>
  );
};

// Hook tùy chỉnh
export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
};