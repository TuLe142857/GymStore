import axiosClient from "@/utils/axiosClient";

/**
 * Ghi nhận tương tác của người dùng (fire-and-forget).
 * Sẽ tự động đính kèm token nếu người dùng đã đăng nhập.
 * Sẽ tự động bị API từ chối nếu là guest (điều này là mong muốn).
 */
export const logInteraction = (productId: string, type: 'view' | 'add_to_cart' | 'purchase') => {
  // Đảm bảo có productId
  if (!productId) {
    console.warn("logInteraction: Bỏ qua vì thiếu productId");
    return;
  }

  // Gửi request mà không cần đợi (fire-and-forget)
  // Chúng ta không muốn việc log lỗi làm hỏng trải nghiệm người dùng
  axiosClient.post('/interaction/log', {
    product_id: productId,
    type: type,
  }).catch(error => {
    // Chỉ log lỗi ra console để debug
    console.warn(
      `[Interaction Log Failed] Product: ${productId}, Type: ${type}`,
      error.response?.data || error.message
    );
  });
};