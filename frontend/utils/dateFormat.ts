import { formatDistanceToNow } from "date-fns";

export const humanizeDate = (dateString: string) => {
  const date = new Date(dateString);
  return formatDistanceToNow(date, { addSuffix: true });
};

// Add other date formatting utilities as needed
export const formatDate = (
  dateString: string,
  format: string = "MMM dd, yyyy"
) => {
  const date = new Date(dateString);
  return format(date, format);
};
