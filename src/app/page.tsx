import { redirect } from 'next/navigation'

export default function RootPage() {
  // デフォルトロケールにリダイレクト
  redirect('/en-US')
}
