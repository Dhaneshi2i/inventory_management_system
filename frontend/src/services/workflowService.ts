import { apiService } from './api';
import { 
  Inventory, 
  PurchaseOrder, 
  StockMovement, 
  StockAlert,
  Supplier,
  Warehouse,
  Product
} from '@/types';
import { toast } from 'react-hot-toast';

// Workflow Service for handling business logic
export class WorkflowService {
  
  // Inventory Management Workflows
  
  /**
   * Process stock adjustment workflow
   */
  static async processStockAdjustment(
    inventoryId: string, 
    quantity: number, 
    notes: string,
    adjustmentType: 'add' | 'subtract' | 'set'
  ) {
    try {
      // Get current inventory
      const currentInventory = await apiService.get<Inventory>(`/inventory/${inventoryId}/`);
      
      let newQuantity: number;
      switch (adjustmentType) {
        case 'add':
          newQuantity = currentInventory.quantity + quantity;
          break;
        case 'subtract':
          newQuantity = Math.max(0, currentInventory.quantity - quantity);
          break;
        case 'set':
          newQuantity = Math.max(0, quantity);
          break;
        default:
          throw new Error('Invalid adjustment type');
      }
      
      // Update inventory
      const updatedInventory = await apiService.patch<Inventory>(`/inventory/${inventoryId}/`, {
        quantity: newQuantity,
        notes: notes
      });
      
      // Create stock movement record
      await apiService.post<StockMovement>('/stock-movements/', {
        inventory_id: inventoryId,
        movement_type: 'adjustment',
        quantity: Math.abs(newQuantity - currentInventory.quantity),
        notes: notes,
        reference_type: 'adjustment',
        reference_id: Date.now()
      });
      
      // Check for alerts
      await this.checkAndCreateAlerts(updatedInventory);
      
      toast.success('Stock adjustment processed successfully');
      return updatedInventory;
      
    } catch (error) {
      toast.error('Failed to process stock adjustment');
      throw error;
    }
  }
  
  /**
   * Process stock transfer workflow
   */
  static async processStockTransfer(
    fromWarehouseId: string,
    toWarehouseId: string,
    productId: string,
    quantity: number,
    notes: string
  ) {
    try {
      // Get source inventory
      const sourceInventory = await apiService.get<Inventory[]>(`/inventory/`, {
        params: { warehouse_id: fromWarehouseId, product_id: productId }
      });
      
      if (!sourceInventory.results.length || sourceInventory.results[0].quantity < quantity) {
        throw new Error('Insufficient stock for transfer');
      }
      
      // Get destination inventory
      const destInventory = await apiService.get<Inventory[]>(`/inventory/`, {
        params: { warehouse_id: toWarehouseId, product_id: productId }
      });
      
      // Update source inventory
      const sourceItem = sourceInventory.results[0];
      await apiService.patch<Inventory>(`/inventory/${sourceItem.id}/`, {
        quantity: sourceItem.quantity - quantity
      });
      
      // Update or create destination inventory
      if (destInventory.results.length) {
        const destItem = destInventory.results[0];
        await apiService.patch<Inventory>(`/inventory/${destItem.id}/`, {
          quantity: destItem.quantity + quantity
        });
      } else {
        await apiService.post<Inventory>('/inventory/', {
          product_id: productId,
          warehouse_id: toWarehouseId,
          quantity: quantity,
          reorder_point: 10,
          max_stock_level: 100
        });
      }
      
      // Create stock movement records
      await apiService.post<StockMovement>('/stock-movements/', {
        inventory_id: sourceItem.id,
        movement_type: 'transfer_out',
        quantity: quantity,
        notes: `Transfer to ${toWarehouseId}: ${notes}`,
        reference_type: 'transfer',
        reference_id: Date.now()
      });
      
      toast.success('Stock transfer completed successfully');
      
    } catch (error) {
      toast.error('Failed to process stock transfer');
      throw error;
    }
  }
  
  /**
   * Process purchase order workflow
   */
  static async processPurchaseOrder(purchaseOrderData: any) {
    try {
      // Create purchase order
      const purchaseOrder = await apiService.post<PurchaseOrder>('/purchase-orders/', purchaseOrderData);
      
      // Send notification to approver
      await this.sendNotification('purchase_order_created', {
        purchase_order_id: purchaseOrder.id,
        supplier_name: purchaseOrderData.supplier_name,
        total_amount: purchaseOrderData.total_amount
      });
      
      toast.success('Purchase order created successfully');
      return purchaseOrder;
      
    } catch (error) {
      toast.error('Failed to create purchase order');
      throw error;
    }
  }
  
  /**
   * Process purchase order approval workflow
   */
  static async processPurchaseOrderApproval(purchaseOrderId: string, approved: boolean, notes?: string) {
    try {
      const status = approved ? 'approved' : 'rejected';
      
      // Update purchase order status
      const updatedPO = await apiService.patch<PurchaseOrder>(`/purchase-orders/${purchaseOrderId}/`, {
        status: status,
        approved_at: approved ? new Date().toISOString() : null,
        notes: notes
      });
      
      // Send notification to supplier
      await this.sendNotification('purchase_order_status_changed', {
        purchase_order_id: purchaseOrderId,
        status: status,
        supplier_id: updatedPO.supplier.id
      });
      
      toast.success(`Purchase order ${status} successfully`);
      return updatedPO;
      
    } catch (error) {
      toast.error('Failed to process purchase order approval');
      throw error;
    }
  }
  
  /**
   * Process goods receipt workflow
   */
  static async processGoodsReceipt(
    purchaseOrderId: string,
    receivedItems: Array<{ item_id: string; received_quantity: number; notes?: string }>
  ) {
    try {
      // Update purchase order with received quantities
      await apiService.patch<PurchaseOrder>(`/purchase-orders/${purchaseOrderId}/`, {
        received_items: receivedItems
      });
      
      // Update inventory for each received item
      for (const item of receivedItems) {
        const inventory = await apiService.get<Inventory>(`/inventory/${item.item_id}/`);
        
        await apiService.patch<Inventory>(`/inventory/${item.item_id}/`, {
          quantity: inventory.quantity + item.received_quantity
        });
        
        // Create stock movement record
        await apiService.post<StockMovement>('/stock-movements/', {
          inventory_id: item.item_id,
          movement_type: 'in',
          quantity: item.received_quantity,
          notes: `Goods receipt from PO ${purchaseOrderId}: ${item.notes || ''}`,
          reference_type: 'purchase_order',
          reference_id: purchaseOrderId
        });
      }
      
      toast.success('Goods receipt processed successfully');
      
    } catch (error) {
      toast.error('Failed to process goods receipt');
      throw error;
    }
  }
  
  /**
   * Check and create alerts for inventory items
   */
  static async checkAndCreateAlerts(inventory: Inventory) {
    try {
      const alerts = [];
      
      // Check for low stock
      if (inventory.quantity <= inventory.reorder_point && inventory.quantity > 0) {
        alerts.push({
          product_id: inventory.product.id,
          warehouse_id: inventory.warehouse.id,
          alert_type: 'low_stock',
          severity: 'medium',
          message: `${inventory.product.name} is below reorder point`,
          threshold_value: inventory.reorder_point,
          current_value: inventory.quantity
        });
      }
      
      // Check for out of stock
      if (inventory.quantity === 0) {
        alerts.push({
          product_id: inventory.product.id,
          warehouse_id: inventory.warehouse.id,
          alert_type: 'out_of_stock',
          severity: 'high',
          message: `${inventory.product.name} is out of stock`,
          threshold_value: 0,
          current_value: 0
        });
      }
      
      // Check for overstock
      if (inventory.quantity > inventory.max_stock_level) {
        alerts.push({
          product_id: inventory.product.id,
          warehouse_id: inventory.warehouse.id,
          alert_type: 'overstock',
          severity: 'low',
          message: `${inventory.product.name} is overstocked`,
          threshold_value: inventory.max_stock_level,
          current_value: inventory.quantity
        });
      }
      
      // Create alerts
      for (const alertData of alerts) {
        await apiService.post<StockAlert>('/alerts/', alertData);
      }
      
    } catch (error) {
      console.error('Failed to create alerts:', error);
    }
  }
  
  /**
   * Process alert resolution workflow
   */
  static async processAlertResolution(
    alertId: string, 
    resolved: boolean, 
    resolutionNotes?: string
  ) {
    try {
      const updatedAlert = await apiService.patch<StockAlert>(`/alerts/${alertId}/`, {
        is_resolved: resolved,
        resolved_at: resolved ? new Date().toISOString() : null,
        resolution_notes: resolutionNotes
      });
      
      if (resolved) {
        toast.success('Alert resolved successfully');
      }
      
      return updatedAlert;
      
    } catch (error) {
      toast.error('Failed to process alert resolution');
      throw error;
    }
  }
  
  /**
   * Generate reorder recommendations
   */
  static async generateReorderRecommendations() {
    try {
      // Get all low stock items
      const lowStockItems = await apiService.get<Inventory[]>('/inventory/', {
        params: { is_low_stock: true }
      });
      
      const recommendations = [];
      
      for (const item of lowStockItems.results) {
        const recommendedQuantity = item.max_stock_level - item.quantity;
        
        if (recommendedQuantity > 0) {
          recommendations.push({
            product: item.product,
            warehouse: item.warehouse,
            current_quantity: item.quantity,
            recommended_quantity: recommendedQuantity,
            urgency: item.quantity === 0 ? 'critical' : 'medium'
          });
        }
      }
      
      return recommendations;
      
    } catch (error) {
      console.error('Failed to generate reorder recommendations:', error);
      return [];
    }
  }
  
  /**
   * Send notifications
   */
  static async sendNotification(type: string, data: any) {
    try {
      await apiService.post('/notifications/', {
        type: type,
        data: data,
        created_at: new Date().toISOString()
      });
    } catch (error) {
      console.error('Failed to send notification:', error);
    }
  }
  
  /**
   * Generate inventory report
   */
  static async generateInventoryReport(filters?: any) {
    try {
      const inventory = await apiService.get<Inventory[]>('/inventory/', { params: filters });
      
      const report = {
        total_items: inventory.results.length,
        total_value: inventory.results.reduce((sum, item) => {
          const value = parseFloat(item.stock_value.replace('$', '').replace(',', ''));
          return sum + (isNaN(value) ? 0 : value);
        }, 0),
        low_stock_items: inventory.results.filter(item => item.is_low_stock).length,
        out_of_stock_items: inventory.results.filter(item => item.is_out_of_stock).length,
        items: inventory.results
      };
      
      return report;
      
    } catch (error) {
      console.error('Failed to generate inventory report:', error);
      throw error;
    }
  }
  
  /**
   * Process supplier performance analysis
   */
  static async analyzeSupplierPerformance(supplierId: string) {
    try {
      const supplier = await apiService.get<Supplier>(`/suppliers/${supplierId}/`);
      const purchaseOrders = await apiService.get<PurchaseOrder[]>('/purchase-orders/', {
        params: { supplier_id: supplierId }
      });
      
      const analysis = {
        supplier: supplier,
        total_orders: purchaseOrders.results.length,
        total_value: purchaseOrders.results.reduce((sum, po) => {
          const value = parseFloat(po.total_amount.replace('$', '').replace(',', ''));
          return sum + (isNaN(value) ? 0 : value);
        }, 0),
        average_order_value: 0,
        on_time_delivery_rate: 0,
        quality_rating: 0
      };
      
      if (analysis.total_orders > 0) {
        analysis.average_order_value = analysis.total_value / analysis.total_orders;
      }
      
      return analysis;
      
    } catch (error) {
      console.error('Failed to analyze supplier performance:', error);
      throw error;
    }
  }
}

export default WorkflowService; 