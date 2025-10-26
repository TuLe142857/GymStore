
export interface Product {
  id: string | number;
  name: string;
  price: number;
  image: string;
  rating: number;
  // Giả sử API trả về tên category, nếu trả về ID, bạn cần điều chỉnh
  category: string; 
  // Thêm các trường khác nếu API của bạn trả về
  // ví dụ: brand, description...
}

// Định nghĩa kiểu dữ liệu cho danh mục từ API
export interface Category {
  id: string | number;
  name: string;
  // Thêm các trường khác nếu API trả về (ví dụ: image, description)
}

// Kiểu dữ liệu cho response từ API lấy sản phẩm
export interface ProductsApiResponse {
  products: Product[];
  total_pages: number;
  current_page: number;
  total_products: number;
}