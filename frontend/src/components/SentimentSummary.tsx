import { useState, useEffect } from "react";
import axiosClient from "@/utils/axiosClient";

// Định nghĩa kiểu dữ liệu cho JSON trả về
interface SentimentData {
  total_reviews: number;
  summary_percent: {
    positive_pct: number;
    neutral_pct: number;
    negative_pct: number;
  };
}

interface Props {
  productId: string;
}

// Component con cho thanh ProgressBar (để dùng nội bộ)
const ProgressBar = ({
  label,
  percentage,
  colorClass,
}: {
  label: string;
  percentage: number;
  colorClass: string;
}) => (
  <div className="w-full">
    <div className="flex justify-between text-sm font-medium text-muted-foreground mb-1">
      <span>{label}</span>
      <span>{percentage.toFixed(1)}%</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2.5">
      <div
        className={`${colorClass} h-2.5 rounded-full`}
        style={{ width: `${percentage}%` }}
      ></div>
    </div>
  </div>
);

export function SentimentSummary({ productId }: Props) {
  const [summary, setSummary] = useState<SentimentData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Không gọi API nếu không có productId
    if (!productId) {
      setLoading(false);
      return;
    }

    const fetchSentiment = async () => {
      setLoading(true);
      try {
        // Gọi API mới (đã test trên Postman)
        const res = await axiosClient.get(`/sentiment/product/${productId}`);
        setSummary(res.data);
      } catch (err) {
        console.error("Failed to fetch sentiment summary:", err);
        setSummary(null); // Đặt là null nếu lỗi
      } finally {
        setLoading(false);
      }
    };

    fetchSentiment();
  }, [productId]); // Chạy lại khi productId thay đổi

  // ----- Logic hiển thị -----

  // 1. Đang tải
  if (loading) {
    return <p className="text-sm text-muted-foreground">Loading summary...</p>;
  }

  // 2. Lỗi, không có data, hoặc không có review
  if (!summary || summary.total_reviews === 0) {
    // Không hiển thị gì cả
    return null;
  }
  
  const { positive_pct, neutral_pct, negative_pct } = summary.summary_percent;

  // 3. Hiển thị kết quả
  return (
    <div className="space-y-3">
      <ProgressBar
        label="Positive"
        percentage={positive_pct}
        colorClass="bg-green-500" // Màu xanh
      />
      <ProgressBar
        label="Neutral"
        percentage={neutral_pct}
        colorClass="bg-yellow-500" // Màu vàng
      />
      <ProgressBar
        label="Negative"
        percentage={negative_pct}
        colorClass="bg-red-500" // Màu đỏ
      />
      <p className="text-xs text-muted-foreground text-right">
        Based on {summary.total_reviews} reviews
      </p>
    </div>
  );
}