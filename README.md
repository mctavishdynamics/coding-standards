# Coding Standards

A Piton package of rules from well-known coding standards, style guides and programming books. Each rule is one Piton spec. It includes a skill that audits code against the rules you choose.

- **6,456 rules from 76 standards**, covering more than 20 languages plus security, API design, accessibility, commits and design.
- **Each rule is its own file**, with a statement, a rationale, exceptions, good and bad code examples, tags and a link to its source.
- **Every rule is written in our own words**, with new code examples. Nothing is copied from the sources (see [Copyright](#copyright)).
- **The package ships the `coding-standards-audit` skill**, which checks code against the standards you choose and reports each violation with its rule.

## What a rule looks like

Every rule is a `coding-rule` anchor, defined in [`spec/standards/lib/CodingRule.pi`](spec/standards/lib/CodingRule.pi):

```piton
export coding-rule CertCStr31C:
    standard: @{CertC}
    ruleId: STR31-C
    title: Guarantee that storage for strings has sufficient space for character data and the null terminator
    statement:
        Size every string buffer for the longest data it can receive plus the
        terminating null, and use copy and read functions that respect that size.
    rationale:
        Writing past the end of a string buffer is a buffer overflow ...
    exceptions: null
    severity: high
    noncompliant: (fenced code)
    compliant: (fenced code)
    languages: [c]
    tags: [strings, buffer-overflow, memory]
    source: https://cmu-sei.github.io/secure-coding-standards/...
```

| Field | Meaning |
|---|---|
| `standard` | A link to the standard the rule comes from. |
| `ruleId` | The source's own ID (`STR31-C`, `C.21`, `item-12`). When the source has none, it is a section number or a slug of the heading. |
| `title`, `statement`, `rationale` | What to do and why, in plain words. |
| `exceptions` | When the rule does not apply, or `null`. |
| `severity` | Only where the source gives one. Today that is the CERT standards (`low`, `medium`, `high`). Otherwise `null`. |
| `noncompliant`, `compliant` | Short code examples, or `null` when the rule is not about code. |
| `languages` | `[c]`, `[python]` and so on, or `[any]`. |
| `tags` | Topic words. The first tag sometimes has a special meaning (see below). |
| `source` | A link to the rule in the original. |

Some standards use the **first tag** for a special meaning:

| First tag | Meaning |
|---|---|
| `recommendation` | A CERT or ANSSI recommendation: softer guidance than a rule. |
| `practice` | Advice about careers, teams or process rather than code. The audit skill never reports these as findings. |
| `reviewer`, `author` | Google Engineering Practices: whether the rule is for the code reviewer or for the change author. |
| `level-1`, `level-2`, `level-3` | OWASP ASVS verification level. |
| `level-a`, `level-aa`, `level-aaa` | WCAG conformance level. |
| `must`, `should`, `may` | Zalando API guideline strength. |
| `do`, `consider`, `avoid`, `do-not`, `prefer`, `dont` | .NET and Dart guideline strength. |
| `rank-n` | Position in the CWE Top 25 or the OWASP Top 10. |

Each standard is a `coding-standard` anchor ([`spec/standards/lib/CodingStandard.pi`](spec/standards/lib/CodingStandard.pi)). It holds the title, publisher, URL, version and license, and lists its rules in source order.

## Using it in another project

### 1. Install the package

```sh
piton tether <git URL of this repository>
```

This adds the repository to `dependencies` in your `piton.config.pi` and installs the `coding-standards` package into `tethers/coding-standards`. Nothing is fetched at build time. Run `piton update coding-standards` to pull a newer version.

### 2. Get the audit skill

Re-export the skill from your entry file, usually `spec/index.pi`:

```piton
from coding-standards export CodingStandardsAudit
```

Then run `piton build`. With the Claude Code adapter, this writes `.claude/skills/coding-standards-audit/SKILL.md`. Ask for an audit in plain words, or run the skill directly:

```text
/coding-standards-audit src/parser
/coding-standards-audit the current changes, against CERT C and the Power of 10
```

The skill links to every standard, so the build also writes the whole rule library into your reference tree (about 6,500 Markdown files under `.claude/reference/tethers/coding-standards/`). The agent reads only the rules it needs, by following links.

### 3. Or pick rules into your own skills and instructions

Import the rules you want and link to them with `@{...}`. Each link becomes a lazy Markdown link, so the agent opens a rule only when it needs it:

```piton
use @piton/belay

from coding-standards import CertCExp33C, CertCStr31C, PowerOfTen

export skill CReview:
    description: Reviews C code against our chosen rules.
    useWhen: the user asks for a review of C code in this repository
    prompt:
        Check the changed C code against the rules below. Read each rule
        before you report it, and cite its id and source.
    rules:
        - @{CertCStr31C}
        - @{CertCExp33C}
        - every rule listed in @{PowerOfTen}
```

Link to a standard, as `@{PowerOfTen}` does here, to hand over all of its rules. Only what you link to, and what that links to, is written into your reference tree.

To find rule names, browse `tethers/coding-standards/<standard>/` or this repository's compiled reference under `.claude/reference/standards/`. Anchor names start with the standard's prefix, shown in the table below.

## How the audit skill chooses standards

1. It uses the standards you name.
2. Otherwise it uses what the project says it follows: its instructions (`CLAUDE.md`, `AGENTS.md`), its contributing guide, or its tool settings (an ESLint config that extends `airbnb`, a `.clang-format` based on Google or LLVM, a `.rubocop.yml`).
3. Otherwise it uses a default per language: PEP 8 with PEP 257 for Python, CERT C for C, the C++ Core Guidelines with CERT C++ for C++, Airbnb for JavaScript, and so on.

It uses at most one style guide per language, because style guides disagree with each other. It adds security standards on top when the code handles untrusted input or sensitive data. Books and design guidance (Clean Code, the smell catalogues, SOLID and others) are used only when you ask for them. It only reads and reports: it changes code only if you ask it to fix what it found.

The full selection rules are in [`spec/standards/skills/CodingStandardsAudit.pi`](spec/standards/skills/CodingStandardsAudit.pi).

## Standards

| Standard | Anchor | Folder | Rules | License |
|---|---|---|---|---|
| [.NET Framework Design Guidelines](https://learn.microsoft.com/dotnet/standard/design-guidelines/) | `DotnetDesignGuidelines` | `dotnet-design-guidelines` | 369 | CC BY 4.0 for the dotnet/docs repository text (code samples MIT) |
| [A Philosophy of Software Design - Summary of Design Principles and Red Flags](https://web.stanford.edu/~ouster/cgi-bin/book.php) | `PhilosophyOfSoftwareDesign` | `philosophy-of-software-design` | 30 | Copyright John Ousterhout, all rights reserved |
| [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) | `AirbnbJavaScript` | `airbnb-javascript` | 158 | MIT License, Copyright (c) 2012 Airbnb |
| [Airbnb React/JSX Style Guide](https://github.com/airbnb/javascript/tree/master/react) | `AirbnbReact` | `airbnb-react` | 38 | MIT License, Copyright (c) 2012 Airbnb |
| [ANSSI Programming Rules for Secure Software Development in C](https://messervices.cyber.gouv.fr/guides/en-rules-secure-c-language-software-development) | `AnssiC` | `anssi-c` | 193 (55 recommendations) | Licence Ouverte / Open Licence 2.0 (Etalab) |
| [ANSSI Secure Rust Guidelines](https://anssi-fr.github.io/rust-guide/) | `AnssiRust` | `anssi-rust` | 61 (15 recommendations) | Licence Ouverte / Open Licence 2.0 (Etalab) |
| [C++ Coding Standards - 101 Rules, Guidelines, and Best Practices](https://www.informit.com/store/c-plus-plus-coding-standards-101-rules-guidelines-and-9780321113580) | `CppCodingStandards` | `cpp-coding-standards` | 101 | Copyright Pearson Education (Addison-Wesley), Herb Sutter and… |
| [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) | `CppCoreGuidelines` | `cpp-core-guidelines` | 452 | Copyright (c) Standard C++ Foundation and its contributors |
| [Clean Code - A Handbook of Agile Software Craftsmanship, Chapter 17 Smells and Heuristics](https://www.oreilly.com/library/view/clean-code-a/9780136083238/chapter17.html) | `CleanCode` | `clean-code` | 66 | Copyright 2009 Pearson Education, Inc |
| [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) | `ConventionalCommits` | `conventional-commits` | 16 | Creative Commons CC BY 3.0 |
| [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/) | `CweTop25` | `cwe-top-25` | 25 | Copyright The MITRE Corporation |
| [Effective C++](https://www.aristeia.com/books.html) | `EffectiveCpp` | `effective-cpp` | 55 | Copyright Pearson Education (Addison-Wesley), Scott Meyers, all… |
| [Effective Dart](https://dart.dev/effective-dart) | `EffectiveDart` | `effective-dart` | 149 | Text under the Creative Commons Attribution 4.0 License, code… |
| [Effective Go](https://go.dev/doc/effective_go) | `EffectiveGo` | `effective-go` | 71 | Creative Commons Attribution 4.0 for text, BSD license for code |
| [Effective Java](https://www.informit.com/store/effective-java-9780134686097) | `EffectiveJava` | `effective-java` | 90 | Copyright 2018 Pearson Education, Inc., all rights reserved |
| [Effective Modern C++](https://www.aristeia.com/books.html) | `EffectiveModernCpp` | `effective-modern-cpp` | 42 | Copyright Scott Meyers (O'Reilly Media), all rights reserved |
| [Effective Python](https://effectivepython.com/) | `EffectivePython` | `effective-python` | 125 | Copyright 2025 Pearson Education, Inc., all rights reserved |
| [FreeBSD Kernel Source File Style Guide, style(9)](https://man.freebsd.org/cgi/man.cgi?query=style&sektion=9) | `FreeBsdStyle` | `freebsd-style` | 89 | BSD 2-Clause License; Copyright (c) 1995-2025 The FreeBSD Project |
| [GNU Coding Standards](https://www.gnu.org/prep/standards/) | `GnuCodingStandards` | `gnu-coding-standards` | 95 | GNU Free Documentation License 1.3 or later, no Invariant… |
| [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) | `GoCodeReviewComments` | `go-code-review-comments` | 31 | Creative Commons Attribution 4.0 for text, BSD license for code |
| [Go Proverbs](https://go-proverbs.github.io/) | `GoProverbs` | `go-proverbs` | 19 | MIT License, Copyright (c) 2015 go-proverbs |
| [Google API Improvement Proposals](https://google.aip.dev/) | `GoogleAip` | `google-aip` | 65 | CC BY 4.0 for text, Apache 2.0 for code samples |
| [Google C# Style Guide](https://google.github.io/styleguide/csharpguide.html) | `GoogleCSharp` | `google-csharp` | 84 | Creative Commons Attribution 3.0 Unported (CC BY 3.0) |
| [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) | `GoogleCpp` | `google-cpp` | 101 | CC BY 3.0 |
| [Google Engineering Practices - Code Review](https://google.github.io/eng-practices/) | `GoogleEngPractices` | `google-eng-practices` | 71 | CC BY 3.0 |
| [Google Go Style Guide](https://google.github.io/styleguide/go/) | `GoogleGo` | `google-go` | 146 | Creative Commons Attribution 3.0 (CC BY 3.0) |
| [Google HTML/CSS Style Guide](https://google.github.io/styleguide/htmlcssguide.html) | `GoogleHtmlCss` | `google-html-css` | 42 | Creative Commons Attribution 3.0 Unported (CC BY 3.0) |
| [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html) | `GoogleJava` | `google-java` | 70 | CC BY 3.0 (code samples Apache 2.0) |
| [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html) | `GoogleJavaScript` | `google-javascript` | 166 | CC BY 3.0 (code samples Apache 2.0), per the google/styleguide… |
| [Google Objective-C Style Guide](https://google.github.io/styleguide/objcguide.html) | `GoogleObjC` | `google-objc` | 71 | Creative Commons Attribution 3.0 Unported (CC BY 3.0) |
| [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) | `GooglePython` | `google-python` | 70 | Creative Commons Attribution 3.0 Unported (CC BY 3.0) |
| [Google R Style Guide](https://google.github.io/styleguide/Rguide.html) | `GoogleR` | `google-r` | 9 | Creative Commons Attribution 3.0 Unported (CC BY 3.0), adapting… |
| [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) | `GoogleShell` | `google-shell` | 36 | Creative Commons Attribution 3.0 Unported (CC BY 3.0) |
| [Google Swift Style Guide](https://google.github.io/swift/) | `GoogleSwift` | `google-swift` | 86 | Apache License 2.0 |
| [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html) | `GoogleTypeScript` | `google-typescript` | 138 | CC BY 3.0 |
| [How to Write a Git Commit Message](https://cbea.ms/git-commit/) | `CommitMessages` | `commit-messages` | 7 | Copyright Chris Beams, all rights reserved |
| [John Carmack on inlined code and functional style](http://number-none.com/blow/john_carmack_on_inlined_code.html) | `Carmack` | `carmack` | 26 | Copyright John Carmack, all rights reserved |
| [JPL Institutional Coding Standard for the C Programming Language](https://web.archive.org/web/20150215140644/http://lars-lab.jpl.nasa.gov/JPL_Coding_Standard_C.pdf) | `JplC` | `jpl-c` | 31 | Copyright 2009 California Institute of Technology, all rights reserved |
| [Kent Beck's Four Rules of Simple Design](https://martinfowler.com/bliki/BeckDesignRules.html) | `BeckSimpleDesign` | `beck-simple-design` | 4 | Copyright Martin Fowler, all rights reserved |
| [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html) | `KotlinConventions` | `kotlin-conventions` | 70 | Apache-2.0 |
| [Kotlin Library Authors' Guidelines](https://kotlinlang.org/docs/api-guidelines-introduction.html) | `KotlinApiGuidelines` | `kotlin-api-guidelines` | 52 | Apache-2.0 |
| [Linux kernel coding style](https://docs.kernel.org/process/coding-style.html) | `LinuxKernelStyle` | `linux-kernel` | 91 | GPL-2.0-only (part of the Linux kernel documentation, covered by… |
| [LLVM Coding Standards](https://llvm.org/docs/CodingStandards.html) | `LlvmCodingStandards` | `llvm-coding-standards` | 66 | Apache License 2.0 with LLVM Exceptions (llvm-project repository);… |
| [Notes on Programming in C](https://www.cs.princeton.edu/courses/archive/spr01/cs217/pike.html) | `PikeNotes` | `pike-notes` | 15 | Copyright Rob Pike, all rights reserved |
| [OpenBSD Kernel Source File Style Guide, style(9)](https://man.openbsd.org/style.9) | `OpenBsdStyle` | `openbsd-style` | 56 | BSD 2-Clause License; Copyright (c) 1995 FreeBSD Inc., all rights… |
| [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/) | `OwaspAsvs` | `owasp-asvs` | 345 | Creative Commons Attribution-ShareAlike 4.0 International (CC… |
| [OWASP Secure Coding Practices Quick Reference Guide](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/) | `OwaspScp` | `owasp-scp` | 218 | Creative Commons Attribution-ShareAlike 4.0 International (CC… |
| [OWASP Top 10](https://owasp.org/Top10/2025/) | `OwaspTop10` | `owasp-top-10` | 10 | Copyright OWASP Foundation, released under Creative Commons… |
| [PEP 20 - The Zen of Python](https://peps.python.org/pep-0020/) | `ZenOfPython` | `zen-of-python` | 19 | Public domain |
| [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/) | `Pep257` | `pep257` | 16 | Public domain |
| [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/) | `Pep8` | `pep8` | 99 | Public domain |
| [PSR-1 - Basic Coding Standard](https://www.php-fig.org/psr/psr-1/) | `Psr1` | `psr-1` | 10 | Content CC BY 3.0 Unported; code MIT (php-fig/fig-standards… |
| [PSR-12 - Extended Coding Style](https://www.php-fig.org/psr/psr-12/) | `Psr12` | `psr-12` | 84 | Content CC BY 3.0 Unported; code MIT (php-fig/fig-standards… |
| [Refactoring - Improving the Design of Existing Code, Chapter 3 Bad Smells in Code](https://martinfowler.com/books/refactoring.html) | `FowlerRefactoring` | `fowler-refactoring` | 24 | Copyright Martin Fowler / Pearson Education, all rights reserved |
| [Refactoring.Guru - Code Smells](https://refactoring.guru/refactoring/smells) | `RefactoringGuruSmells` | `refactoring-guru-smells` | 23 | Copyright Refactoring.Guru, all rights reserved |
| [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) | `RustApiGuidelines` | `rust-api-guidelines` | 54 | MIT OR Apache-2.0 |
| [Sandi Metz' Rules for Developers](https://thoughtbot.com/blog/sandi-metz-rules-for-developers) | `SandiMetzRules` | `sandi-metz-rules` | 4 | Copyright thoughtbot, inc., all rights reserved |
| [SEI CERT C Coding Standard](https://cmu-sei.github.io/secure-coding-standards/sei-cert-c-coding-standard/) | `CertC` | `cert-c` | 300 (178 recommendations) | Copyright 2026 Carnegie Mellon University |
| [SEI CERT C++ Coding Standard](https://cmu-sei.github.io/secure-coding-standards/sei-cert-cpp-coding-standard/) | `CertCpp` | `cert-cpp` | 83 | Text under Creative Commons Attribution 4.0, code examples under… |
| [SEI CERT Oracle Coding Standard for Java](https://cmu-sei.github.io/secure-coding-standards/sei-cert-oracle-coding-standard-for-java/) | `CertJava` | `cert-java` | 255 (82 recommendations) | CC BY 4.0 for the text and MIT for the code examples, copyright… |
| [Selected writings of Edsger W. Dijkstra](https://www.cs.utexas.edu/~EWD/) | `Dijkstra` | `dijkstra` | 22 | Copyright the heirs of Edsger W. Dijkstra or the respective… |
| [Semantic Versioning](https://semver.org/) | `SemVer` | `semver` | 11 | Creative Commons CC BY 3.0 |
| [SOLID Principles of Object-Oriented Design](https://web.archive.org/web/20151122035331/http://butunclebob.com/ArticleS.UncleBob.PrinciplesOfOod) | `Solid` | `solid` | 5 | Copyright Robert C. Martin, all rights reserved |
| [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/) | `SwiftApiDesign` | `swift-api-design` | 49 | Apache-2.0 with Runtime Library Exception |
| [The Elements of Programming Style](https://en.wikipedia.org/wiki/The_Elements_of_Programming_Style) | `ElementsOfProgrammingStyle` | `elements-of-programming-style` | 77 | Copyright McGraw-Hill, all rights reserved |
| [The Joel Test - 12 Steps to Better Code](https://www.joelonsoftware.com/2000/08/09/the-joel-test-12-steps-to-better-code/) | `JoelTest` | `joel-test` | 12 | Copyright Joel Spolsky, all rights reserved |
| [The Power of 10 - Rules for Developing Safety-Critical Code](https://spinroot.com/gerard/pdf/P10.pdf) | `PowerOfTen` | `nasa-power-of-ten` | 10 | Copyright Gerard J. Holzmann, all rights reserved |
| [The Practice of Programming](https://www.cs.princeton.edu/~bwk/tpop.webpage/) | `PracticeOfProgramming` | `practice-of-programming` | 95 | Copyright Lucent Technologies, all rights reserved |
| [The Pragmatic Programmer - Tips](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/) | `PragmaticProgrammer` | `pragmatic-programmer` | 100 | Copyright The Pragmatic Programmers, LLC, all rights reserved |
| [The Ruby Style Guide](https://rubystyle.guide/) | `RubyStyleGuide` | `ruby-style-guide` | 295 | Creative Commons Attribution 3.0 Unported (CC BY 3.0) |
| [The Twelve-Factor App](https://12factor.net/) | `TwelveFactor` | `twelve-factor` | 12 | MIT |
| [The Unix Philosophy, as stated by Doug McIlroy](https://archive.org/details/bstj57-6-1899) | `McIlroyUnix` | `mcilroy-unix` | 7 | Copyright 1978 AT&T (Bell System Technical Journal) and Peter H.… |
| [Tiger Style](https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md) | `TigerStyle` | `tiger-style` | 72 | Apache License 2.0 |
| [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md) | `UberGo` | `uber-go` | 65 | Apache License 2.0 |
| [Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/) | `Wcag22` | `wcag` | 86 | Copyright 2020-2024 World Wide Web Consortium, W3C Document License |
| [Zalando RESTful API and Event Guidelines](https://opensource.zalando.com/restful-api-guidelines/) | `ZalandoApi` | `zalando-api` | 146 | CC BY 4.0 |

The full scope, every decision and the open questions are in [`spec/standards/CodingStandards.pi`](spec/standards/CodingStandards.pi).

## Copyright

No rule may infringe its source's copyright or license.

- **Our own words:** every statement, rationale and exception says what the source means in new wording and new sentence structure.
- **New code:** every example is newly written. None is copied or lightly edited from the source.
- **Titles:** our own words too. The exception is CERT, whose CC BY 4.0 license allows reuse with attribution and whose titles also serve as the rules' names.
- **Attribution:** every rule links to its source, and every standard records its publisher, version and license.
- **Books:** the rule lists come from each book's own published table of contents or rule summary, checked against public sources. The books' text is never reproduced.
- **Overlap check:** before a standard is accepted, `tools/overlap.py` compares every rule's prose (runs of 7 to 10 words) and its long code lines against the fetched source pages, and anything that matches is rewritten.
- **Left out:** BARR-C, *The Art of Unix Programming* and *97 Things Every Programmer Should Know*, because their licenses forbid derivative works or commercial use. MISRA is left out because it is paid.

This is careful practice, not legal advice. If a source's license matters for your use, check it yourself.

## Working on this repository

The Piton source is the truth. Everything under `.claude/` is generated.

```sh
piton format spec/standards/<standard>   # run per folder; project-wide format stops at 5,000 files
piton check
piton build
```

| Path | What it holds |
|---|---|
| `spec/standards/` | The package root, the part other projects tether. |
| `spec/standards/lib/` | The `coding-rule` and `coding-standard` shapes. |
| `spec/standards/skills/` | The audit skill. |
| `spec/standards/<standard>/` | One standard: its anchor file and one file per rule. A large standard may use subfolders, as the C++ Core Guidelines do. |
| `tools/gen_index.py` | Writes each standard's `index.pi` files and its `rules:` list. |
| `tools/orders/` | The source order of each standard's rules, used by `gen_index.py`. |
| `tools/overlap.py` | The copyright overlap check. Point it at a folder of fetched source pages. |
| `tethers/crux/` | The crux spec skills, used to develop this specification. |

**To add a standard:**

1. Create `spec/standards/<folder>/<Name>.pi` with a `coding-standard` anchor.
2. Add one rule file per rule, named after its anchor, with the standard's prefix (`MyGuideRuleName.pi`). Start each file with `use ../lib/CodingRule` and `from ./<Name> import <Name>`.
3. List the anchor names in source order in `tools/orders/<folder>.txt`.
4. Run `python3 -I tools/gen_index.py spec/standards tools/orders <folder>`, and add `from ./<folder> export *` to `spec/standards/index.pi`.
5. Run the overlap check against the fetched sources and rewrite any hits.
6. Add the standard to the audit skill's `standardsByLanguage`, if it should be used there.
7. Run `piton format`, `piton check` and `piton build`.
