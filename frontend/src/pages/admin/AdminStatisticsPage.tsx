import React, { useEffect, useState } from 'react';
import axiosClient from '../../utils/axiosClient';
import { Button } from "@/components/ui/button";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts';

// --- 1. INTERFACES MỚI ---

// Interface cho từng thẻ Card
interface CardItem {
    label: string;
    value: string | number;
}

// Interface cho data của Chart
interface ChartDataItem {
    label: string;
    value: number | string;
}

interface ChartConfig {
    name: string;
    type: string; // "BarChart" | "PieChart"
    data: ChartDataItem[];
}

// Interface tổng cho response
interface DashboardData {
    cards: CardItem[];
    charts: ChartConfig[];
}

// Config màu sắc cho PieChart
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const AdminStatisticsPage: React.FC = () => {
    const [stats, setStats] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res: any = await axiosClient.get('/admin/statistics');
            const data = res.data ? res.data : res;
            setStats(data);
        } catch (error) {
            console.error("Lỗi tải thống kê:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    // --- HELPER: RENDER CHART (Giữ nguyên) ---
    const renderChartContent = (chart: ChartConfig) => {
        const safeData = chart.data.map(item => ({
            ...item,
            value: Number(item.value) || 0
        }));

        switch (chart.type) {
            case 'BarChart':
                return (
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={safeData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="label" />
                            <YAxis />
                            <Tooltip formatter={(value) => new Intl.NumberFormat('vi-VN').format(Number(value))} />
                            <Legend />
                            <Bar dataKey="value" name={chart.name} fill="#3b82f6" barSize={50} />
                        </BarChart>
                    </ResponsiveContainer>
                );

            case 'PieChart':
                return (
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={safeData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                                nameKey="label"
                            >
                                {safeData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip formatter={(value) => new Intl.NumberFormat('vi-VN').format(Number(value))} />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                );

            default:
                return <div className="flex items-center justify-center h-full text-gray-400">Chart type not supported: {chart.type}</div>;
        }
    };

    return (
        <div className="p-6 bg-gray-50 min-h-screen">
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-800">Thống kê hệ thống</h1>
                <Button onClick={fetchData} variant="outline" className="bg-white hover:bg-gray-100">
                    Làm mới
                </Button>
            </div>

            {loading ? (
                // --- SKELETON LOADING ---
                <div className="space-y-8 animate-pulse">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {[1, 2, 3, 4].map((i) => <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>)}
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="h-80 bg-gray-200 rounded-lg"></div>
                        <div className="h-80 bg-gray-200 rounded-lg"></div>
                    </div>
                </div>
            ) : (
                <div className="space-y-8">
                    {/* 1. CARDS SECTION (CẬP NHẬT LOOP MẢNG) */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {stats?.cards && stats.cards.map((card, index) => (
                            <div
                                key={index}
                                className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
                            >
                                <p className="text-sm font-medium text-gray-500 uppercase tracking-wide truncate mb-1">
                                    {card.label}
                                </p>
                                <p className="text-2xl font-bold text-gray-900 truncate">
                                    {String(card.value)}
                                </p>
                            </div>
                        ))}
                    </div>

                    {/* 2. CHARTS SECTION */}
                    {stats?.charts && stats.charts.length > 0 && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {stats.charts.map((chart, index) => (
                                <div key={index} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-96 flex flex-col">
                                    <h3 className="text-lg font-bold text-gray-800 mb-4">{chart.name}</h3>
                                    <div className="flex-1 w-full min-h-0">
                                        {renderChartContent(chart)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {(!stats?.cards?.length && (!stats?.charts || stats.charts.length === 0)) && (
                        <div className="text-center py-10 text-gray-500">Không có dữ liệu thống kê.</div>
                    )}
                </div>
            )}
        </div>
    );
};

export default AdminStatisticsPage;