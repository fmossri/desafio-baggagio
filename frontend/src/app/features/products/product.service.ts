import { Injectable, inject } from "@angular/core"
import { HttpClient, HttpParams } from "@angular/common/http"
import { Observable } from "rxjs"

import { environment } from "../../../environments/environment"
import type {
    Product,
    ProductCreate,
    ProductListQuery,
    ProductListResponse,
    ProductUpdate,
} from "../../core/models/product.models"

@Injectable({ providedIn: 'root' })
export class ProductService {
    private readonly http = inject(HttpClient);
    private readonly base = `${environment.apiUrl}/products`;

    list(query: ProductListQuery = {}): Observable<ProductListResponse> {
        let p = new HttpParams();
        if (query.skip != null) p = p.set('skip', String(query.skip));
        if (query.limit != null) p = p.set('limit', String(query.limit));
        if (query.q != null && query.q.trim().length > 0) {
            p = p.set('q', query.q.trim());
        }
        if (query.active != null) p = p.set('active', String(query.active));
        if (query.min_price != null) p = p.set('min_price', String(query.min_price));
        if (query.max_price != null) p = p.set('max_price', String(query.max_price));
        if (query.sort != null) p = p.set('sort', query.sort);
        return this.http.get<ProductListResponse>(this.base, { params: p });
    }

    getById(id: string): Observable<Product> {
        return this.http.get<Product>(`${this.base}/${id}`);
    }

    create(body: ProductCreate): Observable<Product> {
        return this.http.post<Product>(this.base, body);
    }

    update(id: string, body: ProductUpdate): Observable<Product> {
        return this.http.put<Product>(`${this.base}/${id}`, body);
    }

    delete(id: string): Observable<void> {
        return this.http.delete<void>(`${this.base}/${id}`);
    }
}