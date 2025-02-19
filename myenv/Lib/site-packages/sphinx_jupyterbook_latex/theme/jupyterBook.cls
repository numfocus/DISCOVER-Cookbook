\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{jupyterBook}[2020/11/06]

% Pass document options defined in config to sphinxmanual.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{sphinxmanual}}
\ProcessOptions\relax

\RequirePackage{xcolor}
\RequirePackage[utf8]{inputenc}
\RequirePackage{graphicx}
\RequirePackage{amsmath, amssymb, amscd}
\RequirePackage{mathrsfs}
\RequirePackage{tikz}
\usetikzlibrary{arrows}
\usetikzlibrary{calc}
\usetikzlibrary{intersections}
\usetikzlibrary{decorations}
\RequirePackage{pgf}
\RequirePackage{pgfplots}
\RequirePackage{bbm}
\def\sphinxdocclass{report}
\LoadClass{sphinxmanual}
\RequirePackage[strict]{changepage}

\setlength{\textwidth}{17.5cm}
\setlength{\textheight}{22cm}
\setlength{\fboxsep}{5pt}

\newcommand{\RR}{\mathbbm R}
\newcommand{\NN}{\mathbbm N}
\newcommand{\PP}{\mathbbm P}
\newcommand{\EE}{\mathbbm E \,}
\newcommand{\XX}{\mathbbm X}
\newcommand{\ZZ}{\mathbbm Z}
\newcommand{\QQ}{\mathbbm Q}
\newcommand{\fF}{\mathcal F}
\newcommand{\dD}{\mathcal D}
\newcommand{\lL}{\mathcal L}
\newcommand{\gG}{\mathcal G}
\newcommand{\hH}{\mathcal H}
\newcommand{\nN}{\mathcal N}
\newcommand{\pP}{\mathcal P}
\newcommand{\BB}{\mathbb B}
\newcommand{\Exp}{\operatorname{Exp}}
\newcommand{\Binomial}{\operatorname{Binomial}}
\newcommand{\Poisson}{\operatorname{Poisson}}
\newcommand{\linop}{\mathcal{L}(\mathbb{B})}
\newcommand{\linopell}{\mathcal{L}(\ell_1)}
\DeclareMathOperator{\trace}{trace}
\DeclareMathOperator{\Var}{Var}
\DeclareMathOperator{\Span}{span}
\DeclareMathOperator{\proj}{proj}
\DeclareMathOperator{\col}{col}
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}
\DeclareMathOperator*{\gt}{>}

\definecolor{codeBlockInputLeftFrame}{RGB}{0,45,74}
\definecolor{CodeBlockInputBorderColor}{RGB}{204,204,204}
\definecolor{CodeBlockInputColor}{RGB}{247,247,247}
\definecolor{CodeBlockOutputBorderColor}{RGB}{247,247,247}
\definecolor{CodeBlockOutputColor}{RGB}{252,252,252}

% This environment at present does not work well with sphinxVerbatim
% TODO: edit this to make a left margin
\newenvironment{leftbarin}
{%
    \def\FrameCommand
    {%
        {\color{codeBlockInputLeftFrame}\vrule width 3pt}%
        \hspace{0pt}%must no space.
        \fboxsep=\FrameSep\colorbox{CodeBlockInputColor}%
    }%
    \MakeFramed{\advance\hsize-\width\@totalleftmargin\z@\linewidth\hsize\@setminipage}%
}
{\endMakeFramed}

% Env which wraps code cell inputs
\newenvironment{sphinxVerbatimInput}
  {\colorlet{VerbatimBorderColor}{CodeBlockInputBorderColor}%
   \colorlet{VerbatimColor}{CodeBlockInputColor}%
   \begin{adjustwidth}{5pt}{}}
  {\end{adjustwidth}}

% Env which wraps code cell outputs
\newenvironment{sphinxVerbatimOutput}
  {\colorlet{VerbatimBorderColor}{CodeBlockOutputBorderColor}%
   \colorlet{VerbatimColor}{CodeBlockOutputColor}%
   \begin{adjustwidth}{20pt}{}}
  {\end{adjustwidth}}
