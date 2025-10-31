
import { useEffect, useState } from "react";
import axiosClient from "@/utils/axiosClient";
import { ProductCard } from "@/components/Product-Card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button"; 
import type { Product } from "@/types"; 

// Định nghĩa kiểu cho pagination
interface Pagination {
  page: number;
  per_page: number;
  total_pages: number;
  total_products: number;
  next_url: string | null;
  prev_url: string | null;
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false); // State cho nút load more
  const [pagination, setPagination] = useState<Pagination | null>(null);

  // Tách hàm fetch data để có thể gọi lại
  const fetchProducts = async (url: string, append = false) => {
    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }

    try {
      const res = await axiosClient.get(url, {
        params: { q: query || null }, // Gửi query 'q' nếu có
      });
      
      if (append) {
        // Nối sản phẩm mới vào danh sách cũ
        setProducts((prev) => [...prev, ...res.data.products]);
      } else {
        // Thay thế danh sách sản phẩm
        setProducts(res.data.products);
      }
      setPagination(res.data.pagination);

    } catch (error) {
      console.error("Failed to fetch products", error);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  // Tải sản phẩm lần đầu (trang 1)
  useEffect(() => {
    // Thêm debounce (delay) để không gọi API liên tục khi gõ
    const handler = setTimeout(() => {
      fetchProducts("/product/"); // Luôn fetch lại từ đầu khi query thay đổi
    }, 300); // Đợi 300ms sau khi ngừng gõ

    return () => {
      clearTimeout(handler);
    };
  }, [query]); // Chạy lại khi 'query' thay đổi

  // Hàm xử lý khi nhấn "Load More"
  const handleLoadMore = () => {
    if (pagination?.next_url) {
      // Backend trả về /api/product/?page=2
      const relativeUrl = pagination.next_url.replace("/api", ""); //
      
      fetchProducts(relativeUrl, true);
    }
  };

  // Lọc sản phẩm ở client-side (ĐÃ BỊ XÓA)
  // Backend đã xử lý việc lọc, ta chỉ cần hiển thị `products`

  return (
    <div className="container mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">All Products</h1>
      <div className="max-w-md mb-6">
        <Input
          placeholder="Search products..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map((p) => (
              <ProductCard
                key={p.id}
                id={String(p.id)}
                name={p.name}
                price={p.price}
                image={p.image_url} // Sửa: Dùng image_url từ API
                category={p.category}
                rating={p.rating}
              />
            ))}
          </div>

          {/* === THÊM NÚT LOAD MORE === */}
          {pagination?.next_url && (
            <div className="text-center mt-12">
              <Button
                size="lg"
                onClick={handleLoadMore}
                disabled={loadingMore}
              >
                {loadingMore ? "Loading..." : "Load More Products"}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}