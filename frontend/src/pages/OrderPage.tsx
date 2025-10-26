import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axiosClient from "@/utils/axiosClient";

export default function OrderPage() {
  const [orders, setOrders] = useState<any[]>([]);
  useEffect(() => {
    axiosClient.get("/order/").then((res) => setOrders(res.data));
  }, []);

  return (
    <div className="container mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">My Orders</h1>
      {orders.length === 0 ? (
        <p>No orders yet.</p>
      ) : (
        <div className="space-y-4">
          {orders.map((o) => (
            <div key={o.id} className="border p-4 rounded-lg flex justify-between">
              <div>
                <p>Order #{o.id}</p>
                <p className="text-muted-foreground">
                  {new Date(o.created_at).toLocaleString()}
                </p>
              </div>
              <Link to={`/orders/${o.id}`} className="text-primary hover:underline">
                View Details
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
