import React, { useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  createColumnHelper,
  ColumnDef,
  SortingState,
  flexRender,
} from '@tanstack/react-table';
import { StarIcon } from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';
import { GreekWork } from '@/types/work';

const columnHelper = createColumnHelper<GreekWork>();

interface TableMeta {
  toggleFavorite: (work: GreekWork) => void;
}

const columns: ColumnDef<GreekWork, any>[] = [
  columnHelper.accessor('title', {
    header: 'Title',
    cell: info => info.getValue(),
  }),
  columnHelper.accessor('author', {
    header: 'Author ID',
    cell: info => info.getValue(),
  }),
  columnHelper.accessor('description', {
    header: 'Description',
    cell: info => info.getValue(),
  }),
  columnHelper.accessor('language', {
    header: 'Language',
    cell: info => info.getValue(),
  }),
  columnHelper.display({
    id: 'favorite',
    header: 'Favorite',
    cell: props => (
      <button
        onClick={() => (props.table.options.meta as TableMeta).toggleFavorite(props.row.original)}
        className="p-1 hover:text-yellow-500 transition-colors"
      >
        {props.row.original.isFavorite ? (
          <StarIconSolid className="h-5 w-5 text-yellow-500" />
        ) : (
          <StarIcon className="h-5 w-5" />
        )}
      </button>
    ),
  }),
];

interface WorksTableProps {
  works: GreekWork[];
  onToggleFavorite: (work: GreekWork) => void;
}

export function WorksTable({ works, onToggleFavorite }: WorksTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);

  const table = useReactTable({
    data: works,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    meta: {
      toggleFavorite: onToggleFavorite,
    },
    filterFns: {
      favorites: (row, columnId, filterValue) => {
        if (!filterValue) return true;
        return row.original.isFavorite;
      },
    },
  });

  return (
    <div className="p-4">
      <div className="mb-4 flex gap-4 items-center">
        <input
          type="text"
          value={globalFilter}
          onChange={e => setGlobalFilter(e.target.value)}
          placeholder="Search all columns..."
          className="px-4 py-2 border rounded-lg"
        />
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={showFavoritesOnly}
            onChange={e => setShowFavoritesOnly(e.target.checked)}
            className="form-checkbox"
          />
          Show favorites only
        </label>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {table.getRowModel().rows.map(row => (
              <tr key={row.id} className="hover:bg-gray-50">
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
