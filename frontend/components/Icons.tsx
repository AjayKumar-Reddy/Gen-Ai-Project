import React from 'react';

type IconProps = React.SVGProps<SVGSVGElement> & { size?: number };

function base(size: number, props: IconProps) {
  return {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    'aria-hidden': true,
    ...props,
  };
}

export const SendIcon = ({ size = 18, ...p }: IconProps) => (
  <svg {...base(size, p)}>
    <path d="M5 12h14M13 6l6 6-6 6" />
  </svg>
);

export const ChevronIcon = ({ size = 16, ...p }: IconProps) => (
  <svg {...base(size, p)}>
    <path d="M9 6l6 6-6 6" />
  </svg>
);

export const DocIcon = ({ size = 16, ...p }: IconProps) => (
  <svg {...base(size, p)}>
    <path d="M7 3h7l5 5v13H7z" />
    <path d="M14 3v5h5M10 13h6M10 17h6" />
  </svg>
);

export const AlertIcon = ({ size = 16, ...p }: IconProps) => (
  <svg {...base(size, p)}>
    <path d="M12 9v4M12 17h.01" />
    <path d="M10.3 3.9L2.4 18a2 2 0 001.7 3h15.8a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z" />
  </svg>
);

export const RetryIcon = ({ size = 14, ...p }: IconProps) => (
  <svg {...base(size, p)}>
    <path d="M4 12a8 8 0 0114-5.3L20 9M20 4v5h-5M20 12a8 8 0 01-14 5.3L4 15M4 20v-5h5" />
  </svg>
);

export const PlusIcon = ({ size = 16, ...p }: IconProps) => (
  <svg {...base(size, p)}>
    <path d="M12 5v14M5 12h14" />
  </svg>
);

export const MenuIcon = ({ size = 18, ...p }: IconProps) => (
  <svg {...base(size, p)}>
    <path d="M4 7h16M4 12h16M4 17h16" />
  </svg>
);

export const CloseIcon = ({ size = 18, ...p }: IconProps) => (
  <svg {...base(size, p)}>
    <path d="M6 6l12 12M18 6L6 18" />
  </svg>
);

export const SearchIcon = ({ size = 16, ...p }: IconProps) => (
  <svg {...base(size, p)}>
    <circle cx="11" cy="11" r="6.5" />
    <path d="M16 16l4 4" />
  </svg>
);
