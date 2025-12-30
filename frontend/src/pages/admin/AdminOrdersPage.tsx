import React, { useEffect, useState } from "react";
import { fetchAllOrders, updateOrderStatus } from "@/api/adminOrdersApi.ts";
import type { Order, OrderStatus } from "@/types.ts";
import { Button } from "@/components/ui/button.tsx";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select.tsx";
import { toast } from "sonner";
import { useAuth } from "@/context/auth-context.tsx";
import { Navigate } from "react-router-dom";

const STATUS_OPTIONS: OrderStatus[] = ["PROCESSING", "DELIVERED", "CANCELLED"];

const AdminOrdersPage: React.FC = () => {
  const { role, isLoggedIn } = useAuth();
  if (!isLoggedIn) return <Navigate to="/login" replace />;
  if (role !== "ADMIN") return <Navigate to="/" replace />;

  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const data = await fetchAllOrders();
      setOrders(data);
    } catch {
      toast.error("Cannot load orders");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const handleStatusChange = async (orderId: number, newStatus: OrderStatus) => {
    try {
      await updateOrderStatus(orderId, newStatus);
      toast.success(`Updated order #${orderId} to ${newStatus}`);
      setOrders((prev) =>
        prev.map((o) => (o.id === orderId ? { ...o, status: newStatus } : o))
      );
    } catch {
      toast.error("Failed to update order status");
    }
  };

  if (loading) return <p className="p-6 text-center">Đang tải đơn hàng...</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">📦 Quản lý đơn hàng</h1>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border">
          <thead className="bg-muted text-left">
            <tr>
              <th className="p-3">ID</th>
              <th className="p-3">Khách hàng</th>
              <th className="p-3">Email</th>
              <th className="p-3">Địa chỉ</th>
              <th className="p-3">Tổng tiền</th>
              <th className="p-3">Trạng thái</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id} className="border-t">
                <td className="p-3 font-medium">#{order.id}</td>
                <td className="p-3">{order.user?.name ?? "—"}</td>
                <td className="p-3">{order.user?.email ?? "—"}</td>
                <td className="p-3">{order.address}</td>
                <td className="p-3">{order.total_amount.toLocaleString()}₫</td>
                <td className="p-3">
                  <Select
                    value={order.status}
                    onValueChange={(value: OrderStatus) =>
                      handleStatusChange(order.id, value)
                    }
                  >
                    <SelectTrigger className="w-[150px]">
                      <SelectValue placeholder="Choose status" />
                    </SelectTrigger>
                    <SelectContent>
                      {STATUS_OPTIONS.map((status) => (
                        <SelectItem key={status} value={status}>
                          {status}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminOrdersPage;
