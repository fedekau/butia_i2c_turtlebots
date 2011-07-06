//Autogenerated file using USB4ALL Descriptor generator V1.0  Author: Rafael Fernandez

// I N C L U D E S *********************************************************
#include "system\typedefs.h"
#include "system\usb\usb.h"
#include "usb4all\boot\boot.h" //mia
// U S B  G L O B A L  V A R I A B L E S ***********************************
#pragma udata
byte usb_device_state;          // Device States: DETACHED, ATTACHED, ...
USB_DEVICE_STATUS usb_stat;     // Global USB flags
byte usb_active_cfg;            // Value of current configuration
byte usb_alt_intf[MAX_NUM_INT]; // Array to keep track of the current alternate
                                // setting for each interface ID
byte epOutSize[MAX_EP_NUMBER] = {64,64,64};

byte epInSize[MAX_EP_NUMBER] = {64,64,64};

// U S B  F I X E D  L O C A T I O N  V A R I A B L E S ********************

#pragma udata usbram4=0x400     //See Linker Script,usb4:0x400-0x4FF(256-byte)
// Section A: Buffer Descriptor Table
#if(0 <= MAX_EP_NUMBER)
volatile far BDT ep0Bo;
volatile far BDT ep0Bi;
#endif

#if(1 <= MAX_EP_NUMBER)
volatile far BDT ep1Bo;
volatile far BDT ep1Bi;
#endif

#if(2 <= MAX_EP_NUMBER)
volatile far BDT ep2Bo;
volatile far BDT ep2Bi;
#endif

#if(3 <= MAX_EP_NUMBER)
volatile far BDT ep3Bo;
volatile far BDT ep3Bi;
#endif

#if(4 <= MAX_EP_NUMBER)
volatile far BDT ep4Bo;
volatile far BDT ep4Bi;
#endif

#if(5 <= MAX_EP_NUMBER)
volatile far BDT ep5Bo;
volatile far BDT ep5Bi;
#endif

#if(6 <= MAX_EP_NUMBER)
volatile far BDT ep6Bo;
volatile far BDT ep6Bi;
#endif

#if(7 <= MAX_EP_NUMBER)
volatile far BDT ep7Bo;
volatile far BDT ep7Bi;
#endif

#if(8 <= MAX_EP_NUMBER)
volatile far BDT ep8Bo;
volatile far BDT ep8Bi;
#endif

#if(9 <= MAX_EP_NUMBER)
volatile far BDT ep9Bo;
volatile far BDT ep9Bi;
#endif

#if(10 <= MAX_EP_NUMBER)
volatile far BDT ep10Bo;
volatile far BDT ep10Bi;
#endif

#if(11 <= MAX_EP_NUMBER)
volatile far BDT ep11Bo;
volatile far BDT ep11Bi;
#endif

#if(12 <= MAX_EP_NUMBER)
volatile far BDT ep12Bo;
volatile far BDT ep12Bi;
#endif

#if(13 <= MAX_EP_NUMBER)
volatile far BDT ep13Bo;
volatile far BDT ep13Bi;
#endif

#if(14 <= MAX_EP_NUMBER)
volatile far BDT ep14Bo;
volatile far BDT ep14Bi;
#endif

// Section B: EP0 Buffer Space
volatile far CTRL_TRF_SETUP SetupPkt;
volatile far CTRL_TRF_DATA CtrlTrfData;

// Section C: Endpoints Buffers

volatile far byte ep1_out_buffer[64];
volatile far byte ep1_in_buffer[64];
volatile far byte ep2_out_buffer[64];
volatile far byte ep2_in_buffer[64];
volatile far byte ep3_out_buffer[64];
volatile far byte ep3_in_buffer[64];
#pragma udata

#pragma romdata _rom_usb_endpoints_init
//defino el ROM_MAX_EP_NUMBER igual al define MAX_EP_NUMBER
rom unsigned char ROM_MAX_EP_NUMBER=MAX_EP_NUMBER;

	#pragma code _usb_endpoints_init
#define USBGEN_UEP              UEP1
#define BOOT_UEP                UEP1 //uso endpoint 2 para bootloader
//		defino endpoints usados por el modulo
//		la idea es que los endpoints se inicialicen sin depender del modulo que los use
//		Por ahora dejo los IFNDEF para no cambiar el codigo de initEps
		#ifndef USBGEN_BD_OUT
			#define USBGEN_BD_OUT           ep1Bo
		#endif
		#ifndef USBGEN_BD_IN
			#define USBGEN_BD_IN            ep1Bi
		#endif
void USBInitEPs(void){
UEP1 = EP_OUT_IN|HSHK_EN;             // Enable 2 data pipes
ep1Bo.Cnt = sizeof(ep1_out_buffer);     // Set buffer size
ep1Bo.ADR = (byte*)&ep1_out_buffer;     // Set buffer address
ep1Bo.Stat._byte = _USIE|_DAT0|_DTSEN;// Set status
ep1Bi.ADR = (byte*)&ep1_in_buffer;      // Set buffer address
ep1Bi.Stat._byte = _UCPU|_DAT1;      // Set buffer status
UEP2 = EP_OUT_IN|HSHK_EN;             // Enable 2 data pipes
ep2Bo.Cnt = sizeof(ep2_out_buffer);     // Set buffer size
ep2Bo.ADR = (byte*)&ep2_out_buffer;     // Set buffer address
ep2Bo.Stat._byte = _USIE|_DAT0|_DTSEN;// Set status
ep2Bi.ADR = (byte*)&ep2_in_buffer;      // Set buffer address
ep2Bi.Stat._byte = _UCPU|_DAT1;      // Set buffer status
UEP3 = EP_OUT_IN|HSHK_EN;             // Enable 2 data pipes
ep3Bo.Cnt = sizeof(ep3_out_buffer);     // Set buffer size
ep3Bo.ADR = (byte*)&ep3_out_buffer;     // Set buffer address
//ep3Bo.Stat._byte = _USIE|_DAT0|_DTSEN;// Set status
ep3Bo.Stat._byte = _USIE|_DAT0;// Set status
ep3Bi.ADR = (byte*)&ep3_in_buffer;      // Set buffer address
ep3Bi.Stat._byte = _UCPU|_DAT1;      // Set buffer status

//boot_trf_state = WAIT_FOR_CMD;
}//end USBGenInitEP
	#pragma code sys