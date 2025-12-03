import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
  try {
    const { dataUrl } = await req.json();
    if (!dataUrl) {
      return NextResponse.json({ error: 'Missing dataUrl payload' }, { status: 400 });
    }

    const [, base64] = dataUrl.split('base64,');
    if (!base64) {
      return NextResponse.json({ error: 'Invalid dataUrl' }, { status: 400 });
    }

    const buffer = Buffer.from(base64, 'base64');
    const png = `data:image/png;base64,${buffer.toString('base64')}`;

    return NextResponse.json({ dataUrl: png });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unable to convert image' },
      { status: 500 },
    );
  }
}

