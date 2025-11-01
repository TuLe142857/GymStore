import axiosClient from "@/utils/axiosClient";
import type { Order } from "@/types";

export const fetchAllOrders = async (): Promise<Order[]> => {
  const res = await axiosClient.get("/admin/orders");
  return res.data.orders;
};

export const updateOrderStatus = async (orderId: number, status: string) => {
  const res = await axiosClient.put(`/admin/orders/${orderId}/status`, { status });
  return res.data;
};
