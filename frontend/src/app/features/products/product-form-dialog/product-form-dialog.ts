import { 
    Component,
    EventEmitter,
    Input,
    OnChanges,
    Output,
    SimpleChanges,
    inject,
} from '@angular/core';
import {
    FormBuilder,
    ReactiveFormsModule,
    Validators,
} from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { DialogModule } from 'primeng/dialog';
import { InputNumberModule } from 'primeng/inputnumber';
import { InputTextModule } from 'primeng/inputtext';
import { TextareaModule } from 'primeng/textarea';

import type { Product } from '../../../core/models/product.models';
import { ProductService } from '../product.service';
import { UserNotifyService } from '../../../core/notify/user-notify.service';

@Component({
  selector: 'app-product-form-dialog',
  imports: [
    ReactiveFormsModule,
    DialogModule,
    ButtonModule,
    InputTextModule,
    TextareaModule,
    InputNumberModule,
    CheckboxModule,
  ],
  templateUrl: './product-form-dialog.html',
  styleUrl: './product-form-dialog.scss',
})
export class ProductFormDialog implements OnChanges {
    private readonly fb = inject(FormBuilder);
    private readonly productsApi = inject(ProductService);
    private readonly notify = inject(UserNotifyService);

    @Input() visible = false;
    @Output() readonly visibleChange = new EventEmitter<boolean>();

    @Input() product: Product | null = null;

    @Output() readonly saved = new EventEmitter<Product>();

    readonly form = this.fb.nonNullable.group({
        name: [
            '',
            [
                Validators.required,
                Validators.minLength(1),
                Validators.maxLength(255),
            ],
        ],
        description: [''],
        price: [0, [Validators.required, Validators.min(0)]],
        quantity: [0, [Validators.required, Validators.min(0)]],
        active: [true],
    });

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['visible']?.currentValue === true) {
            this.patchForm();
        }
    }

    private patchForm(): void {
        if (this.product) {
            this.form.reset({
                name: this.product.name,
                description: this.product.description,
                price:
                    typeof this.product.price === 'string'
                    ? Number(this.product.price)
                    : this.product.price,
                quantity: this.product.quantity,
                active: this.product.active,
            })
        } else {
            this.form.reset({
                name: '',
                description: '',
                price: 0,
                quantity: 0,
                active: true,
            });
        }
    }

    onVisibleChange(open: boolean): void {
        this.visibleChange.emit(open);
    }

    cancel(): void {
        this.visibleChange.emit(false);
    }

    save(): void {
        if (this.form.invalid) {
            this.form.markAllAsTouched();
            return;
        }

        const value = this.form.getRawValue();

        const done = () => {
            this.notify.success(
                this.product ? 'Salvo' : 'Criado',
                this.product ? 'Produto atualizado.' : 'Produto criado.',
            );
            this.visibleChange.emit(false);
            this.saved.emit();
        };

        const onError = (err: unknown) =>
            this.notify.error(err, { skip401: true });

        if (this.product) {
            this.productsApi
                .update(this.product.id, {
                    name: value.name,
                    description: value.description,
                    price: value.price,
                    quantity: value.quantity,
                    active: value.active,
                })
                .subscribe({ next: done, error: onError });
        } else {
            this.productsApi
                .create({
                    name: value.name,
                    description: value.description,
                    price: value.price,
                    quantity: value.quantity,
                    active: value.active,
                })
                .subscribe({ next: done, error: onError });
        }
    }
}

