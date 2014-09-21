# TODO: probably update patch is incomplete
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if "%{_alt_kernel}" != "%{nil}"
%if 0%{?build_kernels:1}
%{error:alt_kernel and build_kernels are mutually exclusive}
exit 1
%endif
%undefine	with_userspace
%global		_build_kernels		%{alt_kernel}
%else
%global		_build_kernels		%{?build_kernels:,%{?build_kernels}}
%endif

%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		kbrs	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo "BuildRequires:kernel%%{_alt_kernel}-module-build >= 3:2.6.36" ; done)
%define		kpkg	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo %%kernel_pkg ; done)
%define		bkpkg	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo %%build_kernel_pkg ; done)
%define		ikpkg	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo %%install_kernel_pkg ; done)

Summary:	Linux drivers for Gemplus GPR400 / GemPC 400 PCMCIA smart card readers
Summary(pl.UTF-8):	Linuksowe sterowniki do czytników kart procesorowych Gemplus GPR400 / GemPC 400 na PCMCIA
%define	pname	gpr400
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}%{_alt_kernel}}
Version:	0
%define	snap	20130219
%define	rel	0.%{snap}.0.1
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	LGPL v2.1 (IFD driver), GPL v2 (Linux kernel driver)
Group:		Libraries
Source0:	https://github.com/jeansch/gpr400/archive/master/%{pname}-%{snap}.tar.gz
# Source0-md5:	1ced7ca5616c257a0229b400ffcfc822
Patch0:		%{pname}-update.patch
# from http://www.hydromel.net/driver/gpr400/
Source1:	http://www.hydromel.net/driver/gpr400/iccdrv.ZIP
# Source1-md5:	a46a0dd7b26c1c8354c7898bcd2ae7a1
URL:		https://github.com/jeansch/gpr400/
BuildRequires:	pcsc-lite-devel >= 1.2.0
BuildRequires:	rpmbuild(macros) >= 1.678
%{?with_dist_kernel:%{expand:%kbrs}}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PC/SC driver for Gemplus GPR400 / GemPC 400 smart card readers

%description -l pl.UTF-8
Sterownik PC/SC do czytników kart procesorowych Gemplus GPR400 / GemPC
400.

%package -n pcsc-driver-gpr400
Summary:	PC/SC driver for Gemplus GPR400 / GemPC 400 smart card readers
Summary(pl.UTF-8):	Sterownik PC/SC do czytników kart procesorowych Gemplus GPR400 / GemPC 400
Group:		Libraries
Requires:	pcsc-lite

%description -n pcsc-driver-gpr400
PC/SC driver for Gemplus GPR400 / GemPC 400 smart card readers

%description -n pcsc-driver-gpr400 -l pl.UTF-8
Sterownik PC/SC do czytników kart procesorowych Gemplus GPR400 / GemPC
400.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-pcmcia-gpr400\
Summary:	Linux driver for Gemplus GPR400/GemPC 400 smart card readers\
Summary(pl.UTF-8):	Sterownik dla Linuksa do czytników kart procesorowych GemPlus GPR400/GemPC 400\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%if %{with dist_kernel}\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
%endif\
\
%description -n kernel%{_alt_kernel}-pcmcia-gpr400\
Linux driver for Gemplus GPR400/GemPC 400 smart card readers.\
\
This package contains Linux module.\
\
%description -n kernel%{_alt_kernel}-pcmcia-gpr400 -l pl.UTF-8\
Sterownik dla Linuksa do czytników kart procesorowych GemPlus\
GPR400/GemPC 400.\
\
Ten pakiet zawiera moduł jądra Linuksa.\
\
%if %{with kernel}\
%files -n kernel%{_alt_kernel}-pcmcia-gpr400\
%defattr(644,root,root,755)\
/lib/modules/%{_kernel_ver}/kernel/drivers/pcmcia/gpr400_cs.ko*\
%endif\
\
%post	-n kernel%{_alt_kernel}-pcmcia-gpr400\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-pcmcia-gpr400\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%build_kernel_modules -C gpr400_cs -m gpr400_cs KERNELRELEASE=%{_kernel_ver}\
# install to local directory, this makes building for multiple kernels easy\
%install_kernel_modules -D installed -m gpr400_cs/gpr400_cs -d kernel/drivers/pcmcia\
%{nil}

%define install_kernel_pkg()\
%{nil}

%{?with_kernel:%{expand:%kpkg}}

%prep
%setup -q -n %{pname}-master
%patch0 -p1

%build
%if %{with userspace}
CC="%{__cc}" \
CFLAGS="%{rpmcflags}" \
%{__make} -C ifd-gpr400 \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -Wall -fPIC" \
	LD="%{__cc} %{rpmldflags}"
%endif

%{?with_kernel:%{expand:%bkpkg}}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT

%if %{with userspace}
install -D ifd-gpr400/libgpr400_ifd.so $RPM_BUILD_ROOT%{_libdir}/pcsc/drivers/libgpr400_ifd.so
install -d $RPM_BUILD_ROOT/etc/reader.conf.d
cat >$RPM_BUILD_ROOT/etc/reader.conf.d/gpr400.conf <<EOF
FRIENDLYNAME	"Gemplus GPR400"
DEVICEFILE	/dev/gpr400
LIBPATH		%{_libdir}/pcsc/drivers/libgpr400_ifd.so
CHANNELID	5
EOF
%endif

%if %{with kernel}
%{expand:%ikpkg}
cp -a installed/* $RPM_BUILD_ROOT
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%files -n pcsc-driver-gpr400
%defattr(644,root,root,755)
%doc ifd-gpr400/README
%attr(755,root,root) %{_libdir}/pcsc/drivers/libgpr400_ifd.so
%config(noreplace) %verify(not md5 mtime size) /etc/reader.conf.d/gpr400.conf
%endif
