import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { useCategories, useCreateCategory, useUpdateCategory, useDeleteCategory } from '@/hooks/useApi';
import { Category } from '@/types';
import DataTable from '@/components/DataTable';
import Modal from '@/components/Modal';
import ConfirmationDialog from '@/components/ConfirmationDialog';
import LoadingSpinner from '@/components/LoadingSpinner';

interface CategoryFormData {
  name: string;
  description: string;
}

const CategoriesPage: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: categoriesData, isLoading } = useCategories();
  const createCategoryMutation = useCreateCategory();
  const updateCategoryMutation = useUpdateCategory();
  const deleteCategoryMutation = useDeleteCategory();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,
  } = useForm<CategoryFormData>();

  const handleCreate = (data: CategoryFormData) => {
    createCategoryMutation.mutate(data, {
      onSuccess: () => {
        setIsCreateModalOpen(false);
        reset();
      },
    });
  };

  const handleEdit = (data: CategoryFormData) => {
    if (selectedCategory) {
      updateCategoryMutation.mutate(
        { id: selectedCategory.id, data },
        {
          onSuccess: () => {
            setIsEditModalOpen(false);
            setSelectedCategory(null);
            reset();
          },
        }
      );
    }
  };

  const handleDelete = () => {
    if (selectedCategory) {
      deleteCategoryMutation.mutate(selectedCategory.id, {
        onSuccess: () => {
          setIsDeleteModalOpen(false);
          setSelectedCategory(null);
        },
      });
    }
  };

  const openEditModal = (category: Category) => {
    setSelectedCategory(category);
    setValue('name', category.name);
    setValue('description', category.description);
    setIsEditModalOpen(true);
  };

  const openDeleteModal = (category: Category) => {
    setSelectedCategory(category);
    setIsDeleteModalOpen(true);
  };

  const columns = [
    {
      key: 'name',
      label: 'Name',
      sortable: true,
    },
    {
      key: 'description',
      label: 'Description',
      sortable: true,
    },
    {
      key: 'product_count',
      label: 'Products',
      sortable: true,
      render: (value: number) => (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          {value}
        </span>
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

  const filteredCategories = categoriesData?.results.filter(category =>
    category.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    category.description.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const actions = (category: Category) => (
    <div className="flex items-center space-x-2">
      <button
        onClick={() => openEditModal(category)}
        className="text-primary-600 hover:text-primary-900"
      >
        <PencilIcon className="h-4 w-4" />
      </button>
      <button
        onClick={() => openDeleteModal(category)}
        className="text-red-600 hover:text-red-900"
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
          <h1 className="text-2xl font-bold text-gray-900">Categories</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage product categories and organization
          </p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn-primary"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Category
        </button>
      </div>

      {/* Categories Table */}
      <DataTable
        data={filteredCategories}
        columns={columns}
        searchable
        searchPlaceholder="Search categories..."
        onSearch={setSearchQuery}
        sortable
        actions={actions}
        emptyMessage="No categories found"
      />

      {/* Create Category Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create Category"
        size="md"
      >
        <form onSubmit={handleSubmit(handleCreate)} className="space-y-4">
          <div>
            <label className="form-label">Name</label>
            <input
              type="text"
              {...register('name', { required: 'Name is required' })}
              className={`input ${errors.name ? 'input-error' : ''}`}
              placeholder="Enter category name"
            />
            {errors.name && (
              <p className="form-error">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label className="form-label">Description</label>
            <textarea
              {...register('description')}
              rows={3}
              className="input"
              placeholder="Enter category description"
            />
          </div>

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
              disabled={createCategoryMutation.isPending}
              className="btn-primary"
            >
              {createCategoryMutation.isPending ? 'Creating...' : 'Create Category'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Category Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Category"
        size="md"
      >
        <form onSubmit={handleSubmit(handleEdit)} className="space-y-4">
          <div>
            <label className="form-label">Name</label>
            <input
              type="text"
              {...register('name', { required: 'Name is required' })}
              className={`input ${errors.name ? 'input-error' : ''}`}
              placeholder="Enter category name"
            />
            {errors.name && (
              <p className="form-error">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label className="form-label">Description</label>
            <textarea
              {...register('description')}
              rows={3}
              className="input"
              placeholder="Enter category description"
            />
          </div>

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
              disabled={updateCategoryMutation.isPending}
              className="btn-primary"
            >
              {updateCategoryMutation.isPending ? 'Updating...' : 'Update Category'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDelete}
        title="Delete Category"
        message={`Are you sure you want to delete "${selectedCategory?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
        loading={deleteCategoryMutation.isPending}
      />
    </div>
  );
};

export default CategoriesPage; 