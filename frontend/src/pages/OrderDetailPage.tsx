import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axiosClient from "@/utils/axiosClient";
import type { Order, OrderItem, Product } from "@/types";
import { Button } from "@/components/ui/button";
import { FeedbackForm } from "@/components/FeedbackForm";

// 🔧 Kiểu dữ liệu cho OrderDetail
interface OrderDetail extends Order {
  items: (OrderItem & { product: Product })[];
}

// ⚙️ Backend URL (tương thích Docker)
const STATIC_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://backend_service:5000";

// 🧩 Hàm chuẩn hóa URL ảnh
const getCorrectImageUrl = (imagePath: string) => {
  if (!imagePath) return "/placeholder.svg";
  if (imagePath.startsWith("http")) return imagePath;

  const filename = imagePath.replace("/uploads/", "");
  return `${STATIC_BASE_URL}/api/upload/${filename}`;
};

export default function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedbackProductId, setFeedbackProductId] = useState<string | null>(
    null
  );

  useEffect(() => {
    const fetchOrder = async () => {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        // 🧠 Đảm bảo route khớp với backend (/api/order/<id>)
        const res = await axiosClient.get(`/order/${id}`);
        setOrder(res.data);
      } catch (err: any) {
        console.error("Failed to load order:", err);
        setError(err.response?.data?.error || "Failed to load order details.");
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [id]);

  // 🟢 Sau khi feedback thành công
  const handleFeedbackSuccess = () => {
    alert("Thank you for your feedback!");
    setFeedbackProductId(null);
  };

  if (loading)
    return (
      <p className="container mx-auto py-12 px-4 text-center">
        Loading order details...
      </p>
    );

  if (error)
    return (
      <p className="container mx-auto py-12 px-4 text-center text-red-500">
        {error}
      </p>
    );

  if (!order)
    return (
      <p className="container mx-auto py-12 px-4 text-center">
        Order not found.
      </p>
    );

  const isDelivered = order.status === "DELIVERED";

  return (
    <div className="container mx-auto py-12 px-4 max-w-4xl">
      {/* 🧾 Thông tin chung */}
      <h1 className="text-3xl font-bold mb-2">Order #{order.id}</h1>
      <p className="text-muted-foreground mb-4">
        Placed on: {new Date(order.created_at).toLocaleString()}
      </p>
      <p className="font-medium mb-6">
        Status:{" "}
        <span
          className={`font-bold ${
            isDelivered ? "text-green-600" : "text-yellow-600"
          }`}
        >
          {order.status}
        </span>
      </p>

      {/* 📦 Danh sách sản phẩm trong đơn */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Items in this order</h2>

        {order.items.map((item) => (
          <div key={item.id} className="border p-4 rounded-lg">
            <div className="flex flex-col sm:flex-row items-start justify-between">
              {/* 🖼 Thông tin sản phẩm */}
              <div className="flex gap-4 mb-4 sm:mb-0">
                <img
                  src={getCorrectImageUrl(item.product.image)}
                  alt={item.product.name}
                  className="w-20 h-20 object-cover rounded"
                />
                <div>
                  <Link
                    to={`/product/${item.product.id}`}
                    className="font-semibold hover:underline"
                  >
                    {item.product.name}
                  </Link>
                  <p className="text-sm text-muted-foreground">
                    Quantity: {item.quantity}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Price: ${item.price_at_purchase.toFixed(2)}
                  </p>
                </div>
              </div>

              {/* ✍️ Nút Feedback hoặc Form Feedback */}
              {isDelivered && (
                <div className="w-full sm:w-auto flex-shrink-0">
                  {feedbackProductId === String(item.product.id) ? (
                    <div className="w-full max-w-md p-4 bg-gray-50 rounded">
                      <FeedbackForm
                        productId={String(item.product.id)}
                        onFeedbackSubmit={handleFeedbackSuccess}
                      />
                      <Button
                        variant="link"
                        size="sm"
                        onClick={() => setFeedbackProductId(null)}
                        className="mt-2"
                      >
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <Button
                      variant="outline"
                      onClick={async () => {
                        try {
                          const res = await axiosClient.get(`/feedback/check/${item.product.id}`);
                          if (res.data.has_reviewed) {
                            alert("You have already reviewed this product.");
                          }else {
                            setFeedbackProductId(String(item.product.id));
                          }
                        }catch (error) {
                          console.error("Error checking feedback:", error);
                          alert("An error occurred while checking feedback.");
                        }
                      }}
                    >
                      Write a Review
                    </Button>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 💰 Tổng tiền & Địa chỉ giao hàng */}
      <div className="mt-6 border-t pt-6">
        <h3 className="text-lg font-semibold">
          Total: ${order.total_amount.toFixed(2)}
        </h3>
        <p className="text-muted-foreground mt-2">
          Shipping to: {order.address}
        </p>
      </div>
    </div>
  );
}
