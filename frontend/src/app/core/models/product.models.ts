export interface Product {
    id: string;
    name: string;
    description: string;
    price: string;
    quantity: number;
    active: boolean;
    created_at: string;
    updated_at: string;
}

export interface ProductCreate {
    name: string;
    description: string;
    price: number;
    quantity: number;
    active: boolean;
}

export interface ProductUpdate {
    name?: string;
    description?: string;
    price?: number;
    quantity?: number;
    active?: boolean;
}

export type ProductSort =
| "created_at_desc"
| "created_at_asc"
| "price_asc"
| "price_desc"
| "name_asc"
| "name_desc";

export interface ProductListQuery {
    skip?: number;
    limit?: number;
    q?: string;
    active?: boolean;
    min_price?: number;
    max_price?: number;
    sort?: ProductSort;
}

export interface ProductListResponse {
    items: Product[];
    total: number;
}
