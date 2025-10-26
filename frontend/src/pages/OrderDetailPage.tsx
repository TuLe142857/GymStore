import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import axiosClient from "@/utils/axiosClient";

export default function OrderDetailPage() {
  const { id } = useParams();
  const [order, setOrder] = useState<any>(null);

  useEffect(() => {
    if (id) {
      axiosClient
        .get(`/order/${id}`)
        .then((res) => setOrder(res.data))
        .catch((err) => console.error("Failed to fetch order:", err));
    }
  }, [id]);

  if (!order) return <p className="text-center py-8">Loading order details...</p>;

  return (
    <div className="container mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-4">Order #{order.id}</h1>
      <p className="text-gray-600 mb-2">
        Created at: {new Date(order.created_at).toLocaleString()}
      </p>
      <p className="text-gray-600 mb-2">Status: {order.status}</p>
      <p className="text-gray-600 mb-2">Total: ${order.total_amount}</p>

      <h2 className="text-xl font-semibold mt-6 mb-2">Items</h2>
      <ul className="space-y-3">
        {order.items.map((item: any) => (
          <li key={item.id} className="border p-3 rounded-lg">
            <div className="flex justify-between">
              <span>{item.product?.name}</span>
              <span>
                {item.quantity} × ${item.price_at_purchase}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
