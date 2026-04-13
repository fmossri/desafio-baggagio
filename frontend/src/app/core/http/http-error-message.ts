import { HttpErrorResponse } from '@angular/common/http';

export type UserFacingMessage = {
    summary: string;
    detail: string;
    severity: 'error' | 'warn' | 'info' | 'success';
};

const CODE_MESSAGES: Record<string, Pick<UserFacingMessage, 'summary' | 'detail'>> = {
    validation_error: {
        summary: 'Dados inválidos',
        detail: 'Revise os campos e tente novamente.',
    },
    unauthenticated: {
        summary: 'Sessão',
        detail: 'Não foi possível autenticar ou a sessão expirou. Por favor, faça login novamente.',
    },
};

function summarizeValidationDetails(details: unknown): string {
    if (!Array.isArray(details) || details.length === 0) {
        return 'Verifique os campos do formulário.';
    }
    const first = details[0] as { loc?: unknown[]; msg?: string };
    const loc = Array.isArray(first?.loc) ? first.loc.filter((x) => x !== 'body') : [];
    const field = loc.length ? String(loc[loc.length -1]) : 'campo';
    const msg = first?.msg ? String(first.msg) : 'valor inválido';
    return `"${field}": ${msg}`;
}

export function httpErrorToUserMessage(err: unknown): UserFacingMessage {
    if (!(err instanceof HttpErrorResponse)) {
        return {
            severity: 'error',
            summary: 'Erro',
            detail: 'Erro inesperado. Por favor, tente novamente.',
        };
    }
    const body = err.error;

    if (body && typeof body === 'object' && 'code' in body && typeof (body as { code: string }).code === 'string') {
        const code = (body as { code: string}).code;
        const apiMessage = 'message' in body && typeof (body as { message: unknown }).message === 'string'
            ? String((body as { message: string }).message)
            : undefined;

        if (code === 'validation_error' && 'details' in body) {
            return {
                severity: 'error',
                summary: 'Dados inválidos',
                detail: summarizeValidationDetails((body as { details: unknown }).details),
            };
        }
        const mapped = CODE_MESSAGES[code];
        if (mapped) {
            return { severity: 'error', ...mapped};
        }

        if (apiMessage) {
            return { severity: 'error', summary: 'Erro', detail: apiMessage};
        };
    }
    
    if (body && typeof body === 'object' && 'detail' in body) {
        const d = (body as { detail: unknown}).detail;
        if (typeof d === 'string' && d.trim()) {
            return { severity: 'error', summary: 'Erro', detail: d};
        }
    }

    switch (err.status) {
        case 0:
            return {
                severity: 'error',
                summary: 'Conexão',
                detail: 'Não foi possível conectar ao servidor.',
            };
        case 401:
            return {
                severity: 'warn',
                summary: 'Sessão',
                detail: 'Sua sessão expirou. Por favor, faça login novamente.',
            };
        case 403:
            return {
                severity: 'error',
                summary: 'Acesso negado',
                detail: 'Você não tem permissão para acessar este recurso.',
            };
        case 422:
            return {
                severity: 'error',
                summary: 'Validação',
                detail: 'Os dados enviados não são válidos.',
            };
        default:
            return {
                severity: 'error',
                summary: 'Erro',
                detail: 'Não foi possível concluir a operação.',
            };
    }
}