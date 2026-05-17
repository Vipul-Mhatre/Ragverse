export const metadata = {
  title: 'Ragverse Enterprise RAG',
  description: 'Enterprise-secure RAG interface with RBAC and explainability',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'Arial, sans-serif', margin: 24 }}>{children}</body>
    </html>
  );
}
