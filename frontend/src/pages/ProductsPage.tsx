import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { PlusIcon, PencilIcon, TrashIcon, ArrowDownTrayIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline';
import { useProducts, useCategories, useCreateProduct, useUpdateProduct, useDeleteProduct } from '@/hooks/useApi';
import { Product } from '@/types';
import DataTable from '@/components/DataTable';
import Modal from '@/components/Modal';
import ConfirmationDialog from '@/components/ConfirmationDialog';
import ImageUpload from '@/components/ImageUpload';
import LoadingSpinner from '@/components/LoadingSpinner';

interface ProductFormData {
  name: string;
  sku: string;
  category_id: string;
  description: string;
  unit_price: string;
  specifications: string;
}

const ProductsPage: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);

  const { data: productsData, isLoading } = useProducts();
  const { data: categoriesData } = useCategories();
  const createProductMutation = useCreateProduct();
  const updateProductMutation = useUpdateProduct();
  const deleteProductMutation = useDeleteProduct();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,

  } = useForm<ProductFormData>();



  // Generate SKU based on category and name
  const generateSKU = (name: string, categoryId: string) => {
    const category = categoriesData?.results.find(cat => cat.id === categoryId);
    const prefix = category ? category.name.substring(0, 3).toUpperCase() : 'PRD';
    const namePart = name.substring(0, 3).toUpperCase();
    const timestamp = Date.now().toString().slice(-4);
    return `${prefix}-${namePart}-${timestamp}`;
  };

  const handleCreate = (data: ProductFormData) => {
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('sku', data.sku || generateSKU(data.name, data.category_id));
    formData.append('category_id', data.category_id);
    formData.append('description', data.description);
    formData.append('unit_price', data.unit_price);
    
    // Parse specifications JSON
    try {
      const specs = JSON.parse(data.specifications || '{}');
      formData.append('specifications', JSON.stringify(specs));
    } catch {
      formData.append('specifications', '{}');
    }

    if (selectedImage) {
      formData.append('image', selectedImage);
    }

    createProductMutation.mutate(formData as any, {
      onSuccess: () => {
        setIsCreateModalOpen(false);
        reset();
        setSelectedImage(null);
      },
    });
  };

  const handleEdit = (data: ProductFormData) => {
    if (selectedProduct) {
      const formData = new FormData();
      formData.append('name', data.name);
      formData.append('sku', data.sku);
      formData.append('category_id', data.category_id);
      formData.append('description', data.description);
      formData.append('unit_price', data.unit_price);
      
      try {
        const specs = JSON.parse(data.specifications || '{}');
        formData.append('specifications', JSON.stringify(specs));
      } catch {
        formData.append('specifications', '{}');
      }

      if (selectedImage) {
        formData.append('image', selectedImage);
      }

      updateProductMutation.mutate(
        { id: selectedProduct.id, data: formData as any },
        {
          onSuccess: () => {
            setIsEditModalOpen(false);
            setSelectedProduct(null);
            reset();
            setSelectedImage(null);
          },
        }
      );
    }
  };

  const handleDelete = () => {
    if (selectedProduct) {
      deleteProductMutation.mutate(selectedProduct.id, {
        onSuccess: () => {
          setIsDeleteModalOpen(false);
          setSelectedProduct(null);
        },
      });
    }
  };

  const openEditModal = (product: Product) => {
    setSelectedProduct(product);
    setValue('name', product.name);
    setValue('sku', product.sku);
    setValue('category_id', product.category.id);
    setValue('description', product.description);
    setValue('unit_price', product.unit_price);
    setValue('specifications', JSON.stringify(product.specifications, null, 2));
    setIsEditModalOpen(true);
  };

  const openDeleteModal = (product: Product) => {
    setSelectedProduct(product);
    setIsDeleteModalOpen(true);
  };

  const handleExport = () => {
    // Export functionality would be implemented here
    console.log('Export products');
  };

  const handleImport = () => {
    // Import functionality would be implemented here
    console.log('Import products');
  };

  const columns = [
    {
      key: 'name',
      label: 'Product',
      sortable: true,
      render: (_value: string, product: Product) => (
        <div className="flex items-center">
          <div className="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-lg flex items-center justify-center">
            <span className="text-gray-500 text-xs font-medium">
              {product.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="ml-4">
            <div className="text-sm font-medium text-gray-900">{product.name}</div>
            <div className="text-sm text-gray-500">{product.sku}</div>
          </div>
        </div>
      ),
    },
    {
      key: 'category',
      label: 'Category',
      sortable: true,
      render: (value: any) => (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          {value.name}
        </span>
      ),
    },
    {
      key: 'unit_price',
      label: 'Price',
      sortable: true,
      render: (value: string) => (
        <span className="font-medium text-gray-900">${value}</span>
      ),
    },
    {
      key: 'total_value',
      label: 'Total Value',
      sortable: true,
      render: (value: string) => (
        <span className="font-medium text-gray-900">${value}</span>
      ),
    },
    {
      key: 'stock_status',
      label: 'Status',
      sortable: true,
      render: (value: string) => {
        const statusConfig = {
          in_stock: { color: 'bg-green-100 text-green-800', label: 'In Stock' },
          low_stock: { color: 'bg-yellow-100 text-yellow-800', label: 'Low Stock' },
          out_of_stock: { color: 'bg-red-100 text-red-800', label: 'Out of Stock' },
        };
        const config = statusConfig[value as keyof typeof statusConfig] || statusConfig.in_stock;
        return (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
            {config.label}
          </span>
        );
      },
    },
    {
      key: 'created_at',
      label: 'Created',
      sortable: true,
      render: (value: string) => (
        <span className="text-gray-500">
          {new Date(value).toLocaleDateString()}
        </span>
      ),
    },
  ];

  const filteredProducts = productsData?.results.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.sku.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !selectedCategory || product.category.id === selectedCategory;
    return matchesSearch && matchesCategory;
  }) || [];

  const actions = (product: Product) => (
    <div className="flex items-center space-x-2">
      <button
        onClick={() => openEditModal(product)}
        className="text-primary-600 hover:text-primary-900"
        title="Edit"
      >
        <PencilIcon className="h-4 w-4" />
      </button>
      <button
        onClick={() => openDeleteModal(product)}
        className="text-red-600 hover:text-red-900"
        title="Delete"
      >
        <TrashIcon className="h-4 w-4" />
      </button>
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your product catalog and inventory
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleImport}
            className="btn-secondary"
          >
            <ArrowUpTrayIcon className="h-4 w-4 mr-2" />
            Import
          </button>
          <button
            onClick={handleExport}
            className="btn-secondary"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Export
          </button>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="btn-primary"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Product
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search Products
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name or SKU..."
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Category
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input"
            >
              <option value="">All Categories</option>
              {categoriesData?.results.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Products Table */}
      <DataTable
        data={filteredProducts}
        columns={columns}
        searchable={false} // We have custom search above
        sortable
        actions={actions}
        emptyMessage="No products found"
      />

      {/* Create Product Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create Product"
        size="xl"
      >
        <form onSubmit={handleSubmit(handleCreate)} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="form-label">Name</label>
              <input
                type="text"
                {...register('name', { required: 'Name is required' })}
                className={`input ${errors.name ? 'input-error' : ''}`}
                placeholder="Enter product name"
              />
              {errors.name && (
                <p className="form-error">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label className="form-label">SKU</label>
              <input
                type="text"
                {...register('sku')}
                className="input"
                placeholder="Auto-generated if empty"
              />
            </div>
          </div>

          <div>
            <label className="form-label">Category</label>
            <select
              {...register('category_id', { required: 'Category is required' })}
              className={`input ${errors.category_id ? 'input-error' : ''}`}
            >
              <option value="">Select a category</option>
              {categoriesData?.results.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            {errors.category_id && (
              <p className="form-error">{errors.category_id.message}</p>
            )}
          </div>

          <div>
            <label className="form-label">Description</label>
            <textarea
              {...register('description')}
              rows={3}
              className="input"
              placeholder="Enter product description"
            />
          </div>

          <div>
            <label className="form-label">Unit Price</label>
            <input
              type="number"
              step="0.01"
              {...register('unit_price', { 
                required: 'Price is required',
                min: { value: 0, message: 'Price must be positive' }
              })}
              className={`input ${errors.unit_price ? 'input-error' : ''}`}
              placeholder="0.00"
            />
            {errors.unit_price && (
              <p className="form-error">{errors.unit_price.message}</p>
            )}
          </div>

          <div>
            <label className="form-label">Specifications (JSON)</label>
            <textarea
              {...register('specifications')}
              rows={4}
              className="input font-mono text-sm"
              placeholder='{"color": "red", "size": "large", "weight": "2kg"}'
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter specifications as JSON format
            </p>
          </div>

          <ImageUpload
            value={selectedImage}
            onChange={setSelectedImage}
            label="Product Image"
            maxSize={5}
          />

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setIsCreateModalOpen(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createProductMutation.isPending}
              className="btn-primary"
            >
              {createProductMutation.isPending ? 'Creating...' : 'Create Product'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Product Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Product"
        size="xl"
      >
        <form onSubmit={handleSubmit(handleEdit)} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="form-label">Name</label>
              <input
                type="text"
                {...register('name', { required: 'Name is required' })}
                className={`input ${errors.name ? 'input-error' : ''}`}
                placeholder="Enter product name"
              />
              {errors.name && (
                <p className="form-error">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label className="form-label">SKU</label>
              <input
                type="text"
                {...register('sku', { required: 'SKU is required' })}
                className={`input ${errors.sku ? 'input-error' : ''}`}
                placeholder="Enter SKU"
              />
              {errors.sku && (
                <p className="form-error">{errors.sku.message}</p>
              )}
            </div>
          </div>

          <div>
            <label className="form-label">Category</label>
            <select
              {...register('category_id', { required: 'Category is required' })}
              className={`input ${errors.category_id ? 'input-error' : ''}`}
            >
              <option value="">Select a category</option>
              {categoriesData?.results.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            {errors.category_id && (
              <p className="form-error">{errors.category_id.message}</p>
            )}
          </div>

          <div>
            <label className="form-label">Description</label>
            <textarea
              {...register('description')}
              rows={3}
              className="input"
              placeholder="Enter product description"
            />
          </div>

          <div>
            <label className="form-label">Unit Price</label>
            <input
              type="number"
              step="0.01"
              {...register('unit_price', { 
                required: 'Price is required',
                min: { value: 0, message: 'Price must be positive' }
              })}
              className={`input ${errors.unit_price ? 'input-error' : ''}`}
              placeholder="0.00"
            />
            {errors.unit_price && (
              <p className="form-error">{errors.unit_price.message}</p>
            )}
          </div>

          <div>
            <label className="form-label">Specifications (JSON)</label>
            <textarea
              {...register('specifications')}
              rows={4}
              className="input font-mono text-sm"
              placeholder='{"color": "red", "size": "large", "weight": "2kg"}'
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter specifications as JSON format
            </p>
          </div>

          <ImageUpload
            value={selectedImage}
            onChange={setSelectedImage}
            label="Product Image"
            maxSize={5}
          />

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setIsEditModalOpen(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={updateProductMutation.isPending}
              className="btn-primary"
            >
              {updateProductMutation.isPending ? 'Updating...' : 'Update Product'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDelete}
        title="Delete Product"
        message={`Are you sure you want to delete "${selectedProduct?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
        loading={deleteProductMutation.isPending}
      />
    </div>
  );
};

export default ProductsPage; 