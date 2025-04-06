import { NextResponse } from 'next/server';
import { parseWorkMetadata } from '@/utils/xmlParser';
import path from 'path';

export async function GET() {
  try {
    const dataDir = path.join(process.cwd(), 'public/data');
    const works = await parseWorkMetadata(dataDir);
    return NextResponse.json(works);
  } catch (error) {
    console.error('Error fetching works:', error);
    return NextResponse.json(
      { error: 'Failed to fetch works' },
      { status: 500 }
    );
  }
}
