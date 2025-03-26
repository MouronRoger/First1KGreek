import { promises as fs } from 'fs';
import { parseString } from 'xml2js';
import path from 'path';
import { GreekWork } from '@/types/work';

interface TiWork {
  '$': {
    xml_lang: string;
    urn: string;
  };
  'ti:title': Array<{ _: string }>;
  'ti:edition': Array<{
    'ti:description': Array<{ _: string }>;
  }>;
}

interface ParsedXML {
  'ti:work': TiWork;
}

export async function parseWorkMetadata(dirPath: string): Promise<GreekWork[]> {
  const works: GreekWork[] = [];
  
  try {
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    
    for (const entry of entries) {
      if (entry.isDirectory() && entry.name.startsWith('tlg')) {
        const authorId = entry.name;
        const authorPath = path.join(dirPath, authorId);
        const authorWorks = await fs.readdir(authorPath, { withFileTypes: true });
        
        for (const work of authorWorks) {
          if (work.isDirectory()) {
            const metadataPath = path.join(authorPath, work.name, '__cts__.xml');
            try {
              const metadata = await fs.readFile(metadataPath, 'utf-8');
              const parsedWork = await new Promise<ParsedXML>((resolve, reject) => {
                parseString(metadata, (err, result) => {
                  if (err) reject(err);
                  else resolve(result as ParsedXML);
                });
              });
              
              if (parsedWork && parsedWork['ti:work']) {
                const workData = parsedWork['ti:work'];
                const title = workData['ti:title']?.[0]?._ || 'Unknown Title';
                const edition = workData['ti:edition']?.[0];
                const description = edition?.['ti:description']?.[0]?._ || '';
                
                works.push({
                  id: `${authorId}-${work.name}`,
                  title,
                  author: authorId,
                  description,
                  language: workData.$?.xml_lang || 'grc',
                  urn: workData.$?.urn || '',
                  isFavorite: false
                });
              }
            } catch (error) {
              console.error(`Error parsing ${metadataPath}:`, error);
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Error reading directory:', error);
  }
  
  return works;
} 