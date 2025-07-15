export const isHttpError = (
  err: unknown,
): err is { status: number; data?: { detail?: string } } => {
  return typeof err === 'object' && err !== null && 'status' in err
}
