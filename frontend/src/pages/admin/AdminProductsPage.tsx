import React, { useEffect, useState, useRef } from 'react';
import axiosClient from '../../utils/axiosClient';
import { Button } from "@/components/ui/button";

// --- 1. ĐỊNH NGHĨA TYPES TẠI CHỖ (Để không phụ thuộc file khác) ---
interface Brand { id: number; name: string; }
interface Category { id: number; name: string; }
interface Ingredient { id: number; name: string; measurement_unit?: string; }
interface ProductIngredient { id?: number; ingredient_id: number; quantity: number; name?: string; unit?: string; }
interface Product {
    id: number; name: string; desc?: string; price: number; image_url?: string; stock_quantity: number; is_active: boolean;
    category_id: number; brand_id: number;
    package_quantity?: number; package_unit?: string; serving_quantity?: number; serving_unit?: string;
    category_name?: string; brand_name?: string; ingredients?: ProductIngredient[];
}

// --- 2. HELPER COMPONENTS ---
const LoadingSpinner = () => (
    <div className="flex flex-col items-center justify-center p-10">
        <div className="w-10 h-10 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin mb-3"></div>
        <p className="text-gray-500 font-medium">Đang tải dữ liệu...</p>
    </div>
);

// --- 3. COMPONENT CHÍNH ---
const AdminProductsPage = () => {
    // === STATE QUẢN LÝ DỮ LIỆU ===
    const [products, setProducts] = useState<Product[]>([]);
    const [brands, setBrands] = useState<Brand[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [ingredientsList, setIngredientsList] = useState<Ingredient[]>([]);

    // === STATE UI ===
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);

    // === STATE FORM ===
    const [formData, setFormData] = useState({
        name: '', desc: '', price: 0, stock_quantity: 0, category_id: 0, brand_id: 0,
        package_quantity: 0, package_unit: 'lbs', serving_quantity: 0, serving_unit: 'scoops',
        is_active: true, image_url: ''
    });
    const [selectedIngredients, setSelectedIngredients] = useState<ProductIngredient[]>([]);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // === HÀM HỖ TRỢ BÓC TÁCH DỮ LIỆU (FIX LỖI CŨ) ===
    // Hàm này giúp lấy data dù axiosClient trả về kiểu gì
    const getData = (res: any) => {
        return res.data ? res.data : res;
    };

    // === CALL API ===
    const fetchProducts = async (page: number) => {
        setLoading(true);
        try {
            // Gọi API
            const response = await axiosClient.get('/product/', {
                params: { page, per_page: 10, sort_by: 'created_at', order: 'desc' }
            });

            // FIX: Lấy .data thủ công ở đây
            const data = getData(response);

            if (data && data.products) {
                setProducts(data.products);
                setTotalPages(data.pagination?.total_pages || 1);
                setCurrentPage(data.pagination?.page || page);
            } else {
                setProducts([]);
            }
        } catch (error) {
            console.error("Lỗi tải sản phẩm:", error);
        } finally {
            setLoading(false);
        }
    };

    const initData = async () => {
        try {
            // Load các danh mục phụ
            const [resBrands, resCats, resIngs] = await Promise.all([
                axiosClient.get('/product/brands'),
                axiosClient.get('/product/categories'),
                axiosClient.get('/ingredient/')
            ]);

            // FIX: Lấy .data cho từng request
            const brandsData = getData(resBrands);
            const catsData = getData(resCats);
            const ingsData = getData(resIngs);

            setBrands(Array.isArray(brandsData) ? brandsData : []);
            setCategories(Array.isArray(catsData) ? catsData : []);

            const rawIngs = Array.isArray(ingsData) ? ingsData : [];
            setIngredientsList(rawIngs.map((i: any) => ({
                id: i.id, name: i.name, measurement_unit: i.unit || i.measurement_unit
            })));

        } catch (e) { console.error(e); }

        // Load danh sách sản phẩm trang 1
        await fetchProducts(1);
    };

    useEffect(() => { initData(); }, []);

    // === XỬ LÝ SUBMIT ===
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.name || !formData.price || !formData.category_id || !formData.brand_id) {
            alert("Vui lòng điền đủ: Tên, Giá, Danh mục, Thương hiệu");
            return;
        }

        setSubmitting(true);
        try {
            let finalImageUrl = formData.image_url;

            // 1. Upload ảnh (nếu có)
            if (selectedFile) {
                const uploadForm = new FormData();
                uploadForm.append('file', selectedFile);

                const res = await axiosClient.post('/admin/image', uploadForm, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });

                // FIX: Lấy url từ data
                const data = getData(res);
                if (data && data.url) {
                    finalImageUrl = data.url;
                }
            }

            // 2. Tạo Payload
            const payload = {
                ...formData,
                image_url: finalImageUrl,
                ingredients: selectedIngredients.map(ing => ({
                    id: ing.ingredient_id, quantity: ing.quantity
                }))
            };

            // 3. Gửi API
            if (editingId) {
                await axiosClient.put(`/admin/products/${editingId}`, payload);
                alert("Cập nhật thành công!");
            } else {
                await axiosClient.post('/admin/products', payload);
                alert("Thêm mới thành công!");
            }

            closeModal();
            fetchProducts(1); // Reload về trang 1

        } catch (error: any) {
            console.error(error);
            const msg = error.response?.data?.error || "Có lỗi xảy ra";
            alert(`Lỗi: ${msg}`);
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("Bạn muốn ẩn sản phẩm này?")) return;
        try {
            // Hiện chưa có API Delete cứng, dùng tạm logic UI
            alert("Đã gửi yêu cầu ẩn sản phẩm (Cần API Backend hỗ trợ DELETE).");
            // await axiosClient.delete(`/admin/products/${id}`);
            fetchProducts(currentPage);
        } catch (e) { console.error(e); }
    };

    // === FORM HELPERS ===
    const openAddModal = () => {
        setEditingId(null);
        setFormData({ name: '', desc: '', price: 0, stock_quantity: 100, category_id: 0, brand_id: 0, package_quantity: 5, package_unit: 'lbs', serving_quantity: 30, serving_unit: 'scoops', is_active: true, image_url: '' });
        setSelectedIngredients([]);
        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
        setIsModalOpen(true);
    };

    const openEditModal = (p: Product) => {
        setEditingId(p.id);
        setFormData({
            name: p.name, desc: p.desc || '', price: p.price, stock_quantity: p.stock_quantity,
            category_id: p.category_id, brand_id: p.brand_id,
            package_quantity: p.package_quantity || 0, package_unit: p.package_unit || '',
            serving_quantity: p.serving_quantity || 0, serving_unit: p.serving_unit || '',
            is_active: p.is_active, image_url: p.image_url || ''
        });

        // Map ingredients
        if (p.ingredients) {
            setSelectedIngredients(p.ingredients.map(pi => ({
                ingredient_id: pi.id || pi.ingredient_id, quantity: pi.quantity,
                name: ingredientsList.find(i => i.id === (pi.id || pi.ingredient_id))?.name,
                unit: ingredientsList.find(i => i.id === (pi.id || pi.ingredient_id))?.measurement_unit
            })));
        } else {
            setSelectedIngredients([]);
        }
        setIsModalOpen(true);
    };

    const closeModal = () => setIsModalOpen(false);

    // Ingredient Logic
    const addIng = () => {
        if (!ingredientsList.length) return alert("Chưa có danh sách nguyên liệu!");
        const first = ingredientsList[0];
        setSelectedIngredients([...selectedIngredients, { ingredient_id: first.id, quantity: 1, name: first.name, unit: first.measurement_unit }]);
    };
    const updateIng = (idx: number, field: string, val: any) => {
        const list = [...selectedIngredients];
        if (field === 'id') {
            const id = parseInt(val);
            const item = ingredientsList.find(i => i.id === id);
            list[idx] = { ...list[idx], ingredient_id: id, name: item?.name, unit: item?.measurement_unit };
        } else list[idx].quantity = parseFloat(val);
        setSelectedIngredients(list);
    };
    const removeIng = (idx: number) => {
        const list = [...selectedIngredients]; list.splice(idx, 1); setSelectedIngredients(list);
    };

    // === RENDER UI ===
    return (
        <div className="p-6 bg-gray-50 min-h-screen font-sans">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-800">Quản lý Sản phẩm</h1>
                <Button onClick={openAddModal} className="bg-blue-600 hover:bg-blue-700 text-white shadow-lg transition-transform hover:scale-105">
                    + Thêm sản phẩm
                </Button>
            </div>

            {/* BẢNG DỮ LIỆU */}
            <div className="bg-white rounded-lg shadow border overflow-hidden relative min-h-[400px] flex flex-col">
                {loading && (
                    <div className="absolute inset-0 bg-white/90 z-20 flex items-center justify-center">
                        <LoadingSpinner />
                    </div>
                )}

                <div className="overflow-x-auto flex-1">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-gray-100 text-gray-600 uppercase font-bold text-xs">
                        <tr>
                            <th className="p-4 w-16">ID</th>
                            <th className="p-4 w-20">Ảnh</th>
                            <th className="p-4">Tên sản phẩm</th>
                            <th className="p-4">Danh mục / Hãng</th>
                            <th className="p-4 text-right">Giá</th>
                            <th className="p-4 text-center">Kho</th>
                            <th className="p-4 text-center">Trạng thái</th>
                            <th className="p-4 text-right">Thao tác</th>
                        </tr>
                        </thead>
                        <tbody className="divide-y">
                        {!loading && products.length === 0 ? (
                            <tr><td colSpan={8} className="p-10 text-center text-gray-500 italic">Không tìm thấy sản phẩm nào.</td></tr>
                        ) : (
                            products.map(p => (
                                <tr key={p.id} className="hover:bg-blue-50 transition-colors">
                                    <td className="p-4 text-gray-500 font-mono">#{p.id}</td>
                                    <td className="p-4">
                                        <div className="w-12 h-12 rounded border bg-gray-50 overflow-hidden flex items-center justify-center">
                                            {p.image_url ? <img src={p.image_url} className="w-full h-full object-cover"/> : <span className="text-xs text-gray-300">No Img</span>}
                                        </div>
                                    </td>
                                    <td className="p-4 font-semibold text-gray-800 max-w-[220px] truncate" title={p.name}>{p.name}</td>
                                    <td className="p-4">
                                        <div className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded font-medium mb-1 mr-1">
                                            {p.category_name || categories.find(c=>c.id===p.category_id)?.name || 'N/A'}
                                        </div>
                                        <div className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                                            {p.brand_name || brands.find(b=>b.id===p.brand_id)?.name || 'N/A'}
                                        </div>
                                    </td>
                                    <td className="p-4 text-right font-bold text-red-600">{new Intl.NumberFormat('vi-VN').format(p.price)}</td>
                                    <td className="p-4 text-center">
                                            <span className={`px-2 py-1 rounded text-xs font-bold ${p.stock_quantity > 10 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {p.stock_quantity}
                                            </span>
                                    </td>
                                    <td className="p-4 text-center">
                                        {p.is_active ? <span className="text-green-500 text-xs font-bold">● Active</span> : <span className="text-gray-400 text-xs font-bold">● Unactive</span>}
                                    </td>
                                    <td className="p-4 text-right whitespace-nowrap">
                                        <button onClick={() => openEditModal(p)} className="text-blue-600 hover:text-blue-800 font-medium mr-3 transition-colors">Sửa</button>
                                        <button onClick={() => handleDelete(p.id)} className="text-red-500 hover:text-red-700 font-medium transition-colors">Ẩn</button>
                                    </td>
                                </tr>
                            ))
                        )}
                        </tbody>
                    </table>
                </div>

                {/* PAGINATION */}
                {totalPages > 1 && (
                    <div className="p-4 border-t flex justify-between items-center bg-gray-50">
                        <span className="text-sm text-gray-600">Trang <b>{currentPage}</b> / {totalPages}</span>
                        <div className="flex gap-2">
                            <Button variant="outline" size="sm" onClick={() => fetchProducts(currentPage - 1)} disabled={currentPage === 1 || loading}>Trước</Button>
                            <Button variant="outline" size="sm" onClick={() => fetchProducts(currentPage + 1)} disabled={currentPage === totalPages || loading}>Sau</Button>
                        </div>
                    </div>
                )}
            </div>

            {/* === MODAL FORM === */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
                    <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
                        {/* Header */}
                        <div className="px-6 py-4 border-b flex justify-between items-center bg-gray-50">
                            <h3 className="text-lg font-bold text-gray-800">{editingId ? 'Cập nhật Sản phẩm' : 'Thêm Sản phẩm Mới'}</h3>
                            <button onClick={closeModal} className="text-gray-400 hover:text-gray-700 text-2xl font-bold">&times;</button>
                        </div>

                        {/* Body */}
                        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto grid grid-cols-1 md:grid-cols-2 gap-8 bg-white">
                            {/* CỘT TRÁI */}
                            <div className="space-y-5">
                                <div className="space-y-1">
                                    <label className="block text-sm font-semibold text-gray-700">Tên sản phẩm <span className="text-red-500">*</span></label>
                                    <input required className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                                           placeholder="Nhập tên sản phẩm..."
                                           value={formData.name} onChange={e=>setFormData({...formData, name: e.target.value})}/>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1">
                                        <label className="block text-sm font-semibold text-gray-700">Giá bán (VNĐ) <span className="text-red-500">*</span></label>
                                        <input type="number" required className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                               value={formData.price} onChange={e=>setFormData({...formData, price: parseFloat(e.target.value)})}/>
                                    </div>
                                    <div className="space-y-1">
                                        <label className="block text-sm font-semibold text-gray-700">Tồn kho <span className="text-red-500">*</span></label>
                                        <input type="number" required className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                               value={formData.stock_quantity} onChange={e=>setFormData({...formData, stock_quantity: parseInt(e.target.value)})}/>
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1">
                                        <label className="block text-sm font-semibold text-gray-700">Danh mục <span className="text-red-500">*</span></label>
                                        <select className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                                                value={formData.category_id} onChange={e=>setFormData({...formData, category_id: parseInt(e.target.value)})}>
                                            <option value={0}>-- Chọn --</option>
                                            {categories.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}
                                        </select>
                                    </div>
                                    <div className="space-y-1">
                                        <label className="block text-sm font-semibold text-gray-700">Thương hiệu <span className="text-red-500">*</span></label>
                                        <select className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white"
                                                value={formData.brand_id} onChange={e=>setFormData({...formData, brand_id: parseInt(e.target.value)})}>
                                            <option value={0}>-- Chọn --</option>
                                            {brands.map(b=><option key={b.id} value={b.id}>{b.name}</option>)}
                                        </select>
                                    </div>
                                </div>
                                <div className="space-y-1">
                                    <label className="block text-sm font-semibold text-gray-700">Mô tả chi tiết</label>
                                    <textarea rows={4} className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 outline-none"
                                              placeholder="Mô tả về sản phẩm..."
                                              value={formData.desc} onChange={e=>setFormData({...formData, desc: e.target.value})}/>
                                </div>
                            </div>

                            {/* CỘT PHẢI */}
                            <div className="space-y-6">
                                {/* Ảnh */}
                                <div className="space-y-2">
                                    <label className="block text-sm font-semibold text-gray-700">Hình ảnh</label>
                                    <div className="flex gap-4 items-start p-3 border rounded-lg bg-gray-50">
                                        <div className="w-24 h-24 bg-white border rounded-md flex items-center justify-center overflow-hidden shrink-0">
                                            {selectedFile ? <img src={URL.createObjectURL(selectedFile)} className="w-full h-full object-cover"/> :
                                                formData.image_url ? <img src={formData.image_url} className="w-full h-full object-cover"/> : <span className="text-xs text-gray-400">Trống</span>}
                                        </div>
                                        <div className="flex-1">
                                            <input type="file" ref={fileInputRef} onChange={e=>setSelectedFile(e.target.files?.[0]||null)}
                                                   className="block w-full text-sm text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"/>
                                            <p className="text-xs text-gray-500 mt-2">Hỗ trợ JPG, PNG. Ảnh sẽ được upload khi lưu.</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Quy cách */}
                                <div className="space-y-2">
                                    <label className="block text-sm font-semibold text-gray-700">Quy cách đóng gói</label>
                                    <div className="grid grid-cols-2 gap-3 p-3 border rounded-lg bg-gray-50">
                                        <input type="number" placeholder="Trọng lượng (VD: 5)" className="border rounded px-2 py-1 text-sm" value={formData.package_quantity} onChange={e=>setFormData({...formData, package_quantity: parseFloat(e.target.value)})}/>
                                        <input placeholder="Đơn vị (VD: lbs)" className="border rounded px-2 py-1 text-sm" value={formData.package_unit} onChange={e=>setFormData({...formData, package_unit: e.target.value})}/>
                                        <input type="number" placeholder="Số lần dùng (Serving)" className="border rounded px-2 py-1 text-sm" value={formData.serving_quantity} onChange={e=>setFormData({...formData, serving_quantity: parseFloat(e.target.value)})}/>
                                        <input placeholder="Đơn vị (VD: scoops)" className="border rounded px-2 py-1 text-sm" value={formData.serving_unit} onChange={e=>setFormData({...formData, serving_unit: e.target.value})}/>
                                    </div>
                                </div>

                                {/* Thành phần */}
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center">
                                        <label className="block text-sm font-semibold text-gray-700">Thành phần (Ingredients)</label>
                                        <button type="button" onClick={addIng} className="text-xs bg-green-100 text-green-700 font-bold px-2 py-1 rounded hover:bg-green-200 transition">+ Thêm dòng</button>
                                    </div>
                                    <div className="max-h-32 overflow-y-auto space-y-2 border rounded-lg p-2 bg-gray-50">
                                        {selectedIngredients.length === 0 && <p className="text-center text-xs text-gray-400 italic py-2">Chưa có thành phần nào.</p>}
                                        {selectedIngredients.map((row, idx) => (
                                            <div key={idx} className="flex gap-2 items-center">
                                                <select className="border rounded px-2 py-1 text-sm flex-1 bg-white" value={row.ingredient_id} onChange={e=>updateIng(idx, 'id', e.target.value)}>
                                                    {ingredientsList.map(i=><option key={i.id} value={i.id}>{i.name}</option>)}
                                                </select>
                                                <input type="number" className="border rounded px-2 py-1 w-16 text-sm text-center" value={row.quantity} onChange={e=>updateIng(idx, 'qty', e.target.value)}/>
                                                <span className="text-xs text-gray-500 w-8">{row.unit}</span>
                                                <button type="button" onClick={()=>removeIng(idx)} className="text-red-500 font-bold hover:bg-red-100 rounded px-2 transition">&times;</button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Footer */}
                            <div className="col-span-1 md:col-span-2 mt-4 pt-4 border-t flex justify-end gap-3 sticky bottom-0 bg-white">
                                <Button type="button" variant="outline" onClick={closeModal} disabled={submitting}>Hủy bỏ</Button>
                                <Button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white min-w-[140px]" disabled={submitting}>
                                    {submitting ? <div className="flex items-center"><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div> Đang lưu...</div> : 'Lưu sản phẩm'}
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminProductsPage;