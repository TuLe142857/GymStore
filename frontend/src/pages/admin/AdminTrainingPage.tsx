import React, { useEffect, useState } from 'react';
import axiosClient from '../../utils/axiosClient';
import { Button } from "@/components/ui/button";
import {
    Loader2,
    Play,
    CheckCircle2,
    XCircle,
    Clock,
    Brain,
    Search,
    MessageSquare,
    Activity,
    RefreshCw
} from "lucide-react";

// --- 1. TYPES (Khớp với cấu trúc Python trả về) ---
type TaskStatus = "idle" | "running" | "success" | "failed";

interface TaskData {
    status: TaskStatus;
    last_run: number | null; // Python trả về timestamp (seconds)
    message: string;
}

interface TrainingStatusResponse {
    search: TaskData;
    recommendation: TaskData;
    sentiment: TaskData;
}

// Cấu hình hiển thị (Icon, màu sắc, mô tả)
const TASKS_CONFIG = [
    {
        key: 'recommendation' as keyof TrainingStatusResponse,
        title: 'Recommendation Engine',
        description: 'Huấn luyện hệ thống gợi ý sản phẩm (Collaborative/Content-based).',
        icon: Brain,
        color: 'text-purple-600',
        bg: 'bg-purple-100'
    },
    {
        key: 'search' as keyof TrainingStatusResponse,
        title: 'Search Indexing',
        description: 'Đánh lại index tìm kiếm và cập nhật vector embedding.',
        icon: Search,
        color: 'text-blue-600',
        bg: 'bg-blue-100'
    },
    {
        key: 'sentiment' as keyof TrainingStatusResponse,
        title: 'Sentiment Analysis',
        description: 'Phân tích cảm xúc các bình luận/đánh giá mới.',
        icon: MessageSquare,
        color: 'text-pink-600',
        bg: 'bg-pink-100'
    }
];

const AdminTrainingPage = () => {
    // --- STATE ---
    const [statusData, setStatusData] = useState<TrainingStatusResponse | null>(null);
    const [loadingFirstTime, setLoadingFirstTime] = useState(true);
    const [triggeringKey, setTriggeringKey] = useState<string | null>(null);

    // --- API CONFIG ---
    // URL Prefix: Dựa trên admin_bp + training_bp.
    // Ví dụ: Flask prefix là /api/admin -> url là /api/admin/training
    const BASE_URL = '/admin/training';

    // --- HELPER: FETCH DATA ---
    const fetchData = async (isBackground = false) => {
        try {
            if (!isBackground) setLoadingFirstTime(true);

            // GET /admin/training/status
            const res: any = await axiosClient.get(`${BASE_URL}/status`);

            // Xử lý linh hoạt nếu axiosClient trả về data gói trong data
            const data = res.data ? res.data : res;
            setStatusData(data);

        } catch (error) {
            console.error("Lỗi cập nhật trạng thái:", error);
        } finally {
            if (!isBackground) setLoadingFirstTime(false);
        }
    };

    // --- EFFECTS: POLLING ---
    useEffect(() => {
        // 1. Gọi ngay khi vào trang
        fetchData();

        // 2. Tự động cập nhật mỗi 3 giây (Polling)
        // Giúp UI tự đổi từ "Running" -> "Success" mà không cần F5
        const interval = setInterval(() => {
            fetchData(true);
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    // --- ACTION: TRIGGER TRAINING ---
    const handleTrain = async (key: string, title: string) => {
        if (triggeringKey) return; // Chặn spam click

        // Hỏi xác nhận trước khi chạy (Optional, cho an toàn)
        // if (!window.confirm(`Bạn có chắc muốn chạy training cho: ${title}?`)) return;

        setTriggeringKey(key);
        try {
            // POST /admin/training/{key}
            const res: any = await axiosClient.post(`${BASE_URL}/${key}`);

            // Update ngay lập tức state với phản hồi từ server (để hiện loading ngay)
            const data = res.data ? res.data : res;
            setStatusData(data);

            alert(`Đã gửi lệnh chạy thành công: ${title}`);

        } catch (error: any) {
            console.error("Lỗi trigger:", error);
            const msg = error.response?.data?.error || error.message || "Lỗi không xác định";
            alert(`Không thể bắt đầu training: ${msg}`);
        } finally {
            setTriggeringKey(null);
        }
    };

    // --- RENDER HELPERS ---

    // Format thời gian từ timestamp (seconds) sang chuỗi
    const formatTime = (timestamp: number | null) => {
        if (!timestamp) return "Chưa chạy bao giờ";
        try {
            return new Date(timestamp * 1000).toLocaleString('vi-VN', {
                hour: '2-digit', minute: '2-digit', second: '2-digit',
                day: '2-digit', month: '2-digit', year: 'numeric'
            });
        } catch (e) {
            return "Lỗi thời gian";
        }
    };

    // Render Badge trạng thái
    const renderBadge = (status: TaskStatus) => {
        switch (status) {
            case 'running':
                return (
                    <span className="flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-700 border border-yellow-200 animate-pulse">
                        <Loader2 size={12} className="mr-1.5 animate-spin" /> RUNNING
                    </span>
                );
            case 'success':
                return (
                    <span className="flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-green-100 text-green-700 border border-green-200">
                        <CheckCircle2 size={12} className="mr-1.5" /> SUCCESS
                    </span>
                );
            case 'failed':
                return (
                    <span className="flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700 border border-red-200">
                        <XCircle size={12} className="mr-1.5" /> FAILED
                    </span>
                );
            default:
                return (
                    <span className="flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-gray-100 text-gray-600 border border-gray-200">
                        <Activity size={12} className="mr-1.5" /> IDLE
                    </span>
                );
        }
    };

    // --- MAIN RENDER ---
    if (loadingFirstTime && !statusData) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
                <Loader2 className="w-10 h-10 animate-spin text-blue-600 mb-4" />
                <p className="text-gray-500">Đang tải trạng thái hệ thống...</p>
            </div>
        );
    }

    return (
        <div className="p-6 bg-gray-50 min-h-screen font-sans">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800 tracking-tight">System Training Monitor</h1>
                    <p className="text-gray-500 mt-1">Quản lý các tiến trình huấn luyện AI/ML chạy nền (Background Tasks).</p>
                </div>
                <Button
                    variant="outline"
                    onClick={() => fetchData()}
                    className="bg-white hover:bg-gray-100 text-gray-700 border-gray-300"
                >
                    <RefreshCw size={16} className="mr-2" /> Làm mới
                </Button>
            </div>

            {/* Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {TASKS_CONFIG.map((config) => {
                    const taskData = statusData?.[config.key];
                    const currentStatus = taskData?.status || 'idle';
                    const isRunning = currentStatus === 'running';
                    const isProcessing = triggeringKey === config.key;

                    return (
                        <div
                            key={config.key}
                            className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col hover:shadow-md transition-shadow duration-200"
                        >
                            {/* Card Top */}
                            <div className="p-6 border-b border-gray-100 flex-1">
                                <div className="flex justify-between items-start mb-4">
                                    <div className={`p-3 rounded-lg ${config.bg}`}>
                                        <config.icon className={`w-6 h-6 ${config.color}`} />
                                    </div>
                                    {renderBadge(currentStatus)}
                                </div>
                                <h3 className="text-lg font-bold text-gray-900 mb-1">{config.title}</h3>
                                <p className="text-sm text-gray-500 leading-relaxed">
                                    {config.description}
                                </p>
                            </div>

                            {/* Card Middle: Stats & Logs */}
                            <div className="px-6 py-4 bg-gray-50/50 space-y-3">
                                <div className="flex justify-between items-center text-sm border-b border-gray-200 pb-2">
                                    <span className="text-gray-500 flex items-center">
                                        <Clock size={14} className="mr-1.5" /> Lần chạy cuối:
                                    </span>
                                    <span className="font-medium text-gray-700">
                                        {formatTime(taskData?.last_run || null)}
                                    </span>
                                </div>

                                <div>
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                                        Log Message
                                    </span>
                                    <div className={`mt-1 text-xs p-2 rounded border ${
                                        currentStatus === 'failed'
                                            ? 'bg-red-50 text-red-700 border-red-100'
                                            : 'bg-white text-gray-600 border-gray-200'
                                    }`}>
                                        {taskData?.message || "Hệ thống sẵn sàng."}
                                    </div>
                                </div>
                            </div>

                            {/* Card Bottom: Action Button */}
                            <div className="p-4 bg-white border-t border-gray-100 rounded-b-xl">
                                <Button
                                    onClick={() => handleTrain(config.key, config.title)}
                                    disabled={isRunning || isProcessing}
                                    className={`w-full font-medium transition-all duration-200 ${
                                        isRunning
                                            ? 'bg-gray-100 text-gray-400 hover:bg-gray-100 cursor-not-allowed'
                                            : 'bg-gray-900 text-white hover:bg-gray-800 hover:scale-[1.02] active:scale-[0.98]'
                                    }`}
                                >
                                    {isRunning || isProcessing ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            {isProcessing ? "Đang gửi lệnh..." : "Đang xử lý..."}
                                        </>
                                    ) : (
                                        <>
                                            <Play className="mr-2 h-4 w-4 fill-current" />
                                            Bắt đầu Training
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default AdminTrainingPage;