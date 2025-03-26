export interface GreekWork {
  id: string;
  title: string;
  author: string;
  description: string;
  language: string;
  urn: string;
  isFavorite: boolean;
}

export interface WorkMetadata {
  groupUrn: string;
  projid: string;
  urn: string;
  lang: string;
  title: string;
  description: string;
} 