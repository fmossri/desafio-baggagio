import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TableLazyLoadEvent, TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { ToolbarModule } from 'primeng/toolbar';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { TagModule } from 'primeng/tag';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { MessageModule } from 'primeng/message';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';
import { ConfirmationService, MessageService } from 'primeng/api';

import { ProductService } from '../product.service';
import type { Product, ProductSort } from '../../../core/models/product.models';

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [
    FormsModule,
    TableModule,
    ButtonModule,
    ToolbarModule,
    InputTextModule,
    SelectModule,
    TagModule,
    ProgressSpinnerModule,
    MessageModule,
    ConfirmDialogModule,
    ToastModule,
  ],
  providers: [MessageService, ConfirmationService],
  templateUrl: './product-list.html',
  styleUrl: './product-list.scss',
})
export class ProductList implements OnInit {
    private readonly productsApi = inject(ProductService);
    private readonly messages = inject(MessageService);
    private readonly confirm = inject(ConfirmationService);

    products: Product[] = [];
    totalRecords = 0;
    loading = false;
    error: string | null = null;

    filterQ = '';
    filterActive: boolean | null = null;
    filterMinPrice: number | null = null;
    filterMaxPrice: number | null = null;
    sort: ProductSort = 'created_at_desc';

    sortOptions: { label: string; value: ProductSort }[] = [
        { label: 'Mais recentes', value: 'created_at_desc' },
        { label: 'Mais antigos', value: 'created_at_asc' },
        { label: 'Preço ↑', value: 'price_asc'},
        { label: 'Preço ↓', value: 'price_desc'},
        { label: 'Nome A-Z', value: 'name_asc'},
        { label: 'Nome Z-A', value: 'name_desc'},
    ];

    ngOnInit(): void {}

    load(event: TableLazyLoadEvent): void {
        this.loading = true;
        this.error = null;
        const skip = event.first ?? 0;
        const limit = event.rows ?? 10;

        this.productsApi
            .list({
                skip,
                limit,
                q: this.filterQ.trim() || undefined,
                active: this.filterActive ?? undefined,
                min_price: this.filterMinPrice ?? undefined,
                max_price: this.filterMaxPrice ?? undefined,
                sort: this.sort,
            })
            .subscribe({
                next: (res) => {
                    this.products = res.items;
                    this.totalRecords = res.total;
                    this.loading = false;
                },
                error: () => {
                    this.error = "Não foi possível carregar os produtos. Tente novamente.";
                    this.loading = false;
                },
            });
    }

    applyFilters(): void {
        this.load({ first: 0, rows: 10 } as TableLazyLoadEvent);
    }

    confirmDelete(row: Product): void {
        this.confirm.confirm({
            message: `Remover "${row.name}"?`,
            header: 'Confirmar',
            icon: 'pi pi-exclamation-triangle',
            acceptLabel: 'Remover',
            rejectLabel: 'Cancelar',
            accept: () => this.deleteRow(row.id),
        });
    }

    private deleteRow(id: string): void {
        this.productsApi.delete(id).subscribe({
            next: () => {
                this.messages.add({
                    severity: 'success',
                    summary: 'Removido',
                    detail: 'Produto removido.',
                });
                this.applyFilters();
            },
            error: () => {
                this.messages.add({
                    severity: 'error',
                    summary: 'Erro',
                    detail: 'Falha ao remover produto.'
                });
            },
        });
    }
}

