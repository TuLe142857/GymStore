import React, { useEffect, useState, useRef } from 'react';
import axiosClient from '../../utils/axiosClient';
import { Button } from "@/components/ui/button";
// Nếu chưa có shadcn, bạn có thể thay bằng thẻ <button> HTML thường

// --- 1. TYPES (Khớp với DB & API Response) ---
interface CatalogItem {
    id: number;
    name: string;
    // Ingredient fields
    desc?: string;       // Frontend dùng chuẩn 'desc' để map
    measurement_unit?: string; // Frontend dùng chuẩn này để gửi đi
    // Helper fields cho hiển thị
    unit?: string;       // API GET trả về 'unit'
    des?: string;        // API GET trả về 'des'
}

type CatalogType = 'brands' | 'categories' | 'ingredients';

const AdminCatalogsPage = () => {
    // --- STATE ---
    const [activeTab, setActiveTab] = useState<CatalogType>('brands');
    const [data, setData] = useState<CatalogItem[]>([]);
    const [loading, setLoading] = useState(false);

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingItem, setEditingItem] = useState<CatalogItem | null>(null);

    // Form State
    const [formData, setFormData] = useState({
        name: '',
        desc: '',
        measurement_unit: 'g'
    });

    // --- HELPER: XÁC ĐỊNH URL API ---
    // Backend chia làm 2 luồng: GET (Public) và POST/PUT (Admin)
    const getListEndpoint = (type: CatalogType) => {
        // Dựa vào brand_routes.py, category_routes.py...
        // Giả định api_bp prefix là /api. Nếu lỗi 404, thử bỏ /api đi.
        switch (type) {
            case 'brands': return '/brand/';
            case 'categories': return '/category/';
            case 'ingredients': return '/ingredient/';
        }
    };

    const getAdminEndpoint = (type: CatalogType) => {
        // Dựa vào admin_api/catalog.py prefix là /admin
        switch (type) {
            case 'brands': return '/admin/brand';
            case 'categories': return '/admin/category';
            case 'ingredients': return '/admin/ingredient';
        }
    };

    // --- FETCH DATA ---
    const fetchData = async () => {
        setLoading(true);
        try {
            const url = getListEndpoint(activeTab);
            const res: any = await axiosClient.get(url);

            // Backend trả về array trực tiếp hoặc trong data
            const rawData = Array.isArray(res) ? res : (res.data || []);

            // Map dữ liệu để chuẩn hóa (đặc biệt là Ingredient)
            const mappedData = rawData.map((item: any) => ({
                ...item,
                // Ingredient trả về 'des' và 'unit', ta map sang chuẩn để hiển thị
                desc: item.des || item.desc || '',
                measurement_unit: item.unit || item.measurement_unit || ''
            }));

            setData(mappedData);
        } catch (error) {
            console.error("Lỗi tải dữ liệu:", error);
            // alert("Lỗi tải danh sách. Kiểm tra lại API Route.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [activeTab]);

    // --- ACTIONS ---
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const baseUrl = getAdminEndpoint(activeTab);

            // Chuẩn bị payload (JSON vì backend catalog.py dùng request.get_json())
            const payload: any = { name: formData.name };

            // Chỉ gửi thêm field nếu là Ingredient
            if (activeTab === 'ingredients') {
                payload.desc = formData.desc;
                payload.measurement_unit = formData.measurement_unit;
            }

            if (editingItem) {
                // UPDATE (PUT)
                await axiosClient.put(`${baseUrl}/${editingItem.id}`, payload);
            } else {
                // CREATE (POST)
                await axiosClient.post(baseUrl, payload);
            }

            closeModal();
            fetchData(); // Reload lại bảng
            alert(editingItem ? "Cập nhật thành công!" : "Tạo mới thành công!");
        } catch (error: any) {
            console.error("Lỗi lưu:", error);
            const msg = error.response?.data?.error || "Lưu thất bại.";
            alert(`Lỗi: ${msg}`);
        }
    };

    // --- MODAL HANDLERS ---
    const openAddModal = () => {
        setEditingItem(null);
        setFormData({ name: '', desc: '', measurement_unit: 'g' });
        setIsModalOpen(true);
    };

    const openEditModal = (item: CatalogItem) => {
        setEditingItem(item);
        setFormData({
            name: item.name,
            desc: item.desc || '',
            measurement_unit: item.measurement_unit || 'g'
        });
        setIsModalOpen(true);
    };

    const closeModal = () => setIsModalOpen(false);

    // --- RENDER ---
    return (
        <div className="p-6 bg-gray-50 min-h-screen">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">Quản lý Danh mục (Catalog)</h1>

            {/* TABS */}
            <div className="flex gap-2 mb-6 border-b pb-2">
                {(['brands', 'categories', 'ingredients'] as CatalogType[]).map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 font-semibold capitalize rounded-t-lg transition-colors 
                            ${activeTab === tab
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-gray-600 hover:bg-gray-100'}`}
                    >
                        {tab === 'brands' ? 'Thương hiệu' : tab === 'categories' ? 'Danh mục' : 'Thành phần'}
                    </button>
                ))}
            </div>

            {/* TOOLBAR */}
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold capitalize text-gray-700">
                    Danh sách {activeTab}
                </h2>
                <Button onClick={openAddModal} className="bg-blue-600 hover:bg-blue-700 text-white">
                    + Thêm mới
                </Button>
            </div>

            {/* TABLE */}
            <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-100">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">ID</th>
                        <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Tên</th>
                        {activeTab === 'ingredients' && (
                            <>
                                <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Đơn vị</th>
                                <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Mô tả</th>
                            </>
                        )}
                        <th className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase">Hành động</th>
                    </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                    {loading ? (
                        <tr><td colSpan={5} className="text-center py-8">Đang tải...</td></tr>
                    ) : data.length === 0 ? (
                        <tr><td colSpan={5} className="text-center py-8 text-gray-500">Trống</td></tr>
                    ) : (
                        data.map((item) => (
                            <tr key={item.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 text-sm text-gray-500">#{item.id}</td>
                                <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.name}</td>

                                {activeTab === 'ingredients' && (
                                    <>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            <span className="bg-gray-200 px-2 py-1 rounded text-xs">{item.measurement_unit}</span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500 truncate max-w-xs">{item.desc}</td>
                                    </>
                                )}

                                <td className="px-6 py-4 text-right text-sm">
                                    <button
                                        onClick={() => openEditModal(item)}
                                        className="text-blue-600 hover:text-blue-900 font-medium"
                                    >
                                        Sửa
                                    </button>
                                    {/* Backend chưa hỗ trợ API DELETE nên tạm ẩn nút Xóa để tránh lỗi */}
                                    {/* <button className="ml-4 text-red-400 cursor-not-allowed" title="Backend chưa hỗ trợ xóa">Xóa</button> */}
                                </td>
                            </tr>
                        ))
                    )}
                    </tbody>
                </table>
            </div>

            {/* --- MODAL --- */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-hidden animate-in fade-in zoom-in duration-200">
                        <div className="px-6 py-4 border-b bg-gray-50 flex justify-between items-center">
                            <h3 className="text-lg font-bold text-gray-800">
                                {editingItem ? 'Cập nhật' : 'Thêm mới'} {activeTab}
                            </h3>
                            <button onClick={closeModal} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
                        </div>

                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            {/* Field Name (Chung cho tất cả) */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Tên *</label>
                                <input
                                    type="text"
                                    required
                                    className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 outline-none"
                                    value={formData.name}
                                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                                />
                            </div>

                            {/* Các field riêng cho Ingredient */}
                            {activeTab === 'ingredients' && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Đơn vị tính (VD: g, mg, ml) *</label>
                                        <input
                                            type="text"
                                            required
                                            className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 outline-none"
                                            value={formData.measurement_unit}
                                            onChange={(e) => setFormData({...formData, measurement_unit: e.target.value})}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Mô tả</label>
                                        <textarea
                                            className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 outline-none"
                                            rows={3}
                                            value={formData.desc}
                                            onChange={(e) => setFormData({...formData, desc: e.target.value})}
                                        />
                                    </div>
                                </>
                            )}

                            <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
                                <Button type="button" variant="outline" onClick={closeModal}>Hủy</Button>
                                <Button type="submit" className="bg-blue-600 text-white hover:bg-blue-700">
                                    {editingItem ? 'Lưu thay đổi' : 'Tạo mới'}
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminCatalogsPage;