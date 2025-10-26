import React, { createContext, useContext, useState, useEffect } from "react";

// Kiểu dữ liệu từng sản phẩm trong đơn hàng
export interface OrderItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  image: string;
}

// Kiểu dữ liệu của đơn hàng
export interface Order {
  id: string;
  orderNumber: string;
  date: string;
  status: "pending" | "processing" | "shipped" | "delivered" | "cancelled";
  total: number;
  items: OrderItem[];
  shippingAddress: {
    firstName: string;
    lastName: string;
    address: string;
    city: string;
    state: string;
    zip: string;
  };
  trackingNumber?: string;
  estimatedDelivery?: string;
}

// Kiểu dữ liệu context
interface OrdersContextType {
  orders: Order[];
  addOrder: (order: Order) => void;
  getOrder: (id: string) => Order | undefined;
}

// Tạo context
const OrdersContext = createContext<OrdersContextType | undefined>(undefined);

// Một số đơn hàng mẫu để hiển thị ban đầu
const MOCK_ORDERS: Order[] = [
  {
    id: "1",
    orderNumber: "GS-2025-001",
    date: "2025-10-15",
    status: "delivered",
    total: 149.97,
    items: [
      {
        id: "1",
        name: "Whey Protein Isolate",
        price: 49.99,
        quantity: 2,
        image: "/whey-protein-powder.jpg",
      },
      {
        id: "5",
        name: "Multivitamin Complex",
        price: 24.99,
        quantity: 1,
        image: "/multivitamin-pills.png",
      },
    ],
    shippingAddress: {
      firstName: "John",
      lastName: "Doe",
      address: "123 Main St",
      city: "New York",
      state: "NY",
      zip: "10001",
    },
    trackingNumber: "1Z999AA10123456784",
    estimatedDelivery: "2025-10-18",
  },
  {
    id: "2",
    orderNumber: "GS-2025-002",
    date: "2025-10-10",
    status: "shipped",
    total: 89.97,
    items: [
      {
        id: "2",
        name: "Creatine Monohydrate",
        price: 29.99,
        quantity: 3,
        image: "/creatine-supplement.jpg",
      },
    ],
    shippingAddress: {
      firstName: "John",
      lastName: "Doe",
      address: "123 Main St",
      city: "New York",
      state: "NY",
      zip: "10001",
    },
    trackingNumber: "1Z999AA10123456785",
    estimatedDelivery: "2025-10-20",
  },
  {
    id: "3",
    orderNumber: "GS-2025-003",
    date: "2025-10-05",
    status: "processing",
    total: 34.99,
    items: [
      {
        id: "3",
        name: "BCAA Complex",
        price: 34.99,
        quantity: 1,
        image: "/bcaa-amino-acids.jpg",
      },
    ],
    shippingAddress: {
      firstName: "John",
      lastName: "Doe",
      address: "123 Main St",
      city: "New York",
      state: "NY",
      zip: "10001",
    },
  },
];

// Provider chính
export const OrdersProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [isHydrated, setIsHydrated] = useState(false);

  // 🔹 Load dữ liệu từ localStorage khi app khởi động
  useEffect(() => {
    const savedOrders = localStorage.getItem("orders");
    if (savedOrders) {
      try {
        setOrders(JSON.parse(savedOrders));
      } catch (error) {
        console.error("Failed to parse saved orders:", error);
        setOrders(MOCK_ORDERS);
      }
    } else {
      setOrders(MOCK_ORDERS);
    }
    setIsHydrated(true);
  }, []);

  // 🔹 Lưu dữ liệu lại khi có thay đổi
  useEffect(() => {
    if (isHydrated) {
      localStorage.setItem("orders", JSON.stringify(orders));
    }
  }, [orders, isHydrated]);

  // 🔹 Thêm đơn hàng mới
  const addOrder = (order: Order) => {
    setOrders((prevOrders) => [order, ...prevOrders]);
  };

  // 🔹 Lấy đơn hàng theo ID
  const getOrder = (id: string) => {
    return orders.find((order) => order.id === id);
  };

  return (
    <OrdersContext.Provider value={{ orders, addOrder, getOrder }}>
      {children}
    </OrdersContext.Provider>
  );
};

// Hook để dùng context
export const useOrders = (): OrdersContextType => {
  const context = useContext(OrdersContext);
  if (!context) {
    throw new Error("useOrders must be used within an OrdersProvider");
  }
  return context;
};
