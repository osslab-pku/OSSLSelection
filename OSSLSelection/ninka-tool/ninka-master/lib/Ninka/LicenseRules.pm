package Ninka::LicenseRules;

use strict;
use warnings;

our @GENERAL_NON_CRITICAL = ('AllRights');

our @GPL_NON_CRITICAL = (
    'GPLnoVersion',
    'FSFwarranty',
    'LibraryGPLcopyVer0',
    'GPLseeVer0',
    'GPLwrite',
    'SeeFile',
    'FreeSoftware',
    'FSFwarrantyVer0',
    'LibraryGPLseeDetailsVer0',
    'FSFwarranty',
    'LesserGPLseeDetailsVer0',
    'GPLcopyVer0',
    'GNUurl',
    'GPLseeDetailsVer0',
);

our %NON_CRITICAL_RULES = ();

$NON_CRITICAL_RULES{'LGPL-3.0+'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'LGPL-3.0'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'LGPL-2.0+'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'LGPL-2.0'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'LGPL-3.0'} = [@GPL_NON_CRITICAL, 'LesserGPLseeVer3', 'LesserGPLcopyVer3', 'SeeFileVer3'];
$NON_CRITICAL_RULES{'LGPL-2.1+'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'LGPL-2.1'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'LGPL-2.0 or LGPL-3.0'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'LGPL-2.0'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'LGPL-2.0+'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'GPLVer2.1or3KDE+'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'LGPLVer2.1or3KDE+'} = [@GPL_NON_CRITICAL];

$NON_CRITICAL_RULES{'GPL-2.0+'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'GPL-2.0'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'GPL-1.0+'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'GPL-1.0'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'GPL-3.0+'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'GPL-3.0'} = [@GPL_NON_CRITICAL];
$NON_CRITICAL_RULES{'AGPL-3.0'} = [@GPL_NON_CRITICAL, 'AGPLreceivedVer0', 'AGPLseeVer0'];
$NON_CRITICAL_RULES{'AGPL-3.0+'} = [@GPL_NON_CRITICAL, 'AGPLreceivedVer0', 'AGPLseeVer0'];
$NON_CRITICAL_RULES{'GPL-noVersion'} = [@GPL_NON_CRITICAL];

$NON_CRITICAL_RULES{'Apache-1.1'} = ['ApacheLic1_1'];
$NON_CRITICAL_RULES{'Apache-2.0'} = ['ApachePre', 'ApacheSee'];

$NON_CRITICAL_RULES{'LibGCJ'} = ['LibGCJSee'];
$NON_CRITICAL_RULES{'CDDL-1.0'} = ['Compliance', 'CDDLicWhere', 'ApachesPermLim', 'CDDLicIncludeFile', 'UseSubjectToTerm', 'useOnlyInCompliance'];
$NON_CRITICAL_RULES{'CDDL-1.0'} = ['Compliance', 'CDDLicWhere', 'ApachesPermLim', 'CDDLicIncludeFile', 'UseSubjectToTerm', 'useOnlyInCompliance'];

$NON_CRITICAL_RULES{'CDDL-1.0 or GPL-2.0'} = ['CDDLorGPLv2doNotAlter', 'AllRights', 'useOnlyInCompliance', 'CDDLorGPLv2whereVer0', 'ApachesPermLim', 'CDDLorGPLv2include', 'CDDLorGPLv2IfApplicable', 'CDDLorGPLv2Portions', 'CDDLorGPLv2ifYouWishVer2', 'CDDLorGPLv2IfYouAddVer2'];

$NON_CRITICAL_RULES{'CPL-1.0 or GPL-2.0+ or LGPL-2.0+'} = ['licenseBlockBegin', 'licenseBlockEnd'];

$NON_CRITICAL_RULES{'Qt'} = ['Copyright', 'qtNokiaExtra', 'QTNokiaContact', 'qtDiaTems'];
$NON_CRITICAL_RULES{'LGPL-2.1'} = ['LesserqtReviewGPLVer2.1', 'qtLGPLv2.1where'];
$NON_CRITICAL_RULES{'GPL-3.0'} = ['qtReviewGPLVer3.0', 'qtReviewGPLVer3', 'qtGPLwhere'];
$NON_CRITICAL_RULES{'digiaQTExceptionNoticeVer1.1'} = ['qtDigiaExtra'];

$NON_CRITICAL_RULES{'MPL-1.0'} = ['ApacheLicWherePart1', 'MPLwarranty', 'MPLSee'];
$NON_CRITICAL_RULES{'MPL-1.1'} = ['ApacheLicWherePart1', 'MPLwarranty', 'MPLSee'];
$NON_CRITICAL_RULES{'NPL-1.1'} = ['ApacheLicWherePart1', 'MPLwarranty', 'MPLSee'];
$NON_CRITICAL_RULES{'NPL-1_0'} = ['ApacheLicWherePart1', 'MPLwarranty', 'MPLSee'];

$NON_CRITICAL_RULES{'subversion'} = ['SeeFileSVN', 'subversionHistory'];
$NON_CRITICAL_RULES{'subversion+'} = ['SeeFileSVN', 'subversionHistory'];
$NON_CRITICAL_RULES{'TMate+'} = ['SeeFileSVN'];

$NON_CRITICAL_RULES{'openSSL-Variant'} = ['BSDcondAdvPart2'];

$NON_CRITICAL_RULES{'MPL-1.1'} = ['licenseBlockBegin', 'MPLsee', 'Copyright', 'licenseBlockEnd', 'ApacheLicWherePart1', 'MPLwarranty', 'MPLwarrantyVar'];
$NON_CRITICAL_RULES{'MPL1-1 or LGPLv2_1'} = ['MPLoptionIfNotDelete2licsVer0', 'MPL_LGPLseeVer0'];

$NON_CRITICAL_RULES{'FreeType'} = ['FreeTypeNotice'];
$NON_CRITICAL_RULES{'BSL-1.0'} = ['boostSeev1', 'SeeFile'];



1;

__END__

=head1 NAME

Ninka::LicenseRules

=head1 DESCRIPTION

Contains rules used by Ninka::LicenseMatcher.

=head1 COPYRIGHT AND LICENSE

Copyright (C) 2009-2014  Yuki Manabe and Daniel M. German

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

=cut
