// Factory de query keys para TanStack Query — evita strings mágicas espalhadas
export const queryKeys = {
  all: ["{{PROJECT_NAME}}"] as const,
};
